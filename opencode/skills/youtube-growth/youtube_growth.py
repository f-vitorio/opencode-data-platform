#!/usr/bin/env python3
"""
YouTube Growth Manager for OpenCode
Consumes output from video-creator skill to manage YouTube Shorts channel
"""

import os
import sys
import json
import re
import argparse
import hashlib
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import urllib.parse
import subprocess
import shutil

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Warning: Google API libraries not installed. Install with:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Constants
VIDEO_MAKER_DIR = Path("/home/fvitorio/Videos/video-maker")
CREDENTIALS_DIR = Path("/home/fvitorio/.config/opencode/credentials")
TOKEN_FILE = CREDENTIALS_DIR / "youtube-token.json"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "client_secret_1096436543776-iuo52suml8tgdtgvfalnbf15rhmq8kfk.apps.googleusercontent.com.json"
HISTORY_FILE = Path("/home/fvitorio/.config/opencode/skills/youtube-growth/history.json")

# Delimiter used in video-creator metadata files (63 ═ characters)
DELIMITER = "═" * 63

# ── Gate de duração para Shorts (produções novas) ───────────────────────────
# Evidência (10 dias / 22 vídeos): ≤26s = 34,2 views em média | 51–85s = 10,9.
# Vale para NOVOS uploads/agendamentos. Vídeos já publicados não são afetados.
MAX_SHORT_DURATION_S = 30.0
FFPROBE = shutil.which("ffprobe")

# ── TikTok (pacote semi-manual) ─────────────────────────────────────────────
# A publicação é manual: esta skill só prepara a legenda pronta e registra
# o estado local. O limite de legenda do TikTok é 2200 caracteres.
TIKTOK_CAPTION_LIMIT = 2200
TIKTOK_DIR = VIDEO_MAKER_DIR
TIKTOK_HOST_FOLDER = "tiktok-shorts"  # pasta pública no Cloudinary

# ── Links de conversão e UTMs por plataforma ────────────────────────────────
# TikTok NÃO formata URL em legenda nem em comentário: o texto aparece, mas não
# é clicável. O único link clicável orgânico é o da bio (conta Business ou
# pessoal com 1000+ seguidores). Por isso a legenda manda para a bio e traz
# também uma URL curta para quem copiar/colar — essa sim é rastreável.
LANDING_URL = "https://fvs7.com.br/diagnostico-gratuito"

TIKTOK_BIO_URL = (
    f"{LANDING_URL}?utm_source=tiktok&utm_medium=social"
    "&utm_campaign=perfil&utm_content=bio"
)

# Regex pega a URL com ou sem esquema e com ou sem query já montada.
_FVS7_LANDING_RE = re.compile(
    r'(?<![\w.-])(?:(?:https?://)?(?:www\.)?)?'
    r'fvs7\.com\.br/diagnostico-gratuito(?:\?[^\s]*)?'
)


def tiktok_utm_url(slug: str) -> str:
    """URL de conversão com UTM da plataforma TikTok (por vídeo)."""
    clean = re.sub(r'[^a-z0-9_]+', '_', _norm_text(slug)).strip('_') or 'tiktok'
    return (f"{LANDING_URL}?utm_source=tiktok&utm_medium=shorts"
            f"&utm_campaign=tiktok&utm_content={clean}")


def youtube_utm_url(video_id: str, niche: str) -> str:
    """URL de conversão com UTM da plataforma YouTube (por vídeo)."""
    return (f"{LANDING_URL}?utm_source=youtube&utm_medium=shorts"
            f"&utm_campaign={video_id}&utm_content={niche or 'marketing'}")


def probe_duration_seconds(video_path: Path) -> Optional[float]:
    """Duração em segundos via ffprobe. None se ffprobe indisponível/falhar."""
    if not FFPROBE:
        return None
    try:
        out = subprocess.run(
            [FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(video_path)],
            capture_output=True, text=True, timeout=30,
        ).stdout.strip()
        return float(out) if out else None
    except Exception:
        return None


# ── REGRA INVIOLÁVEL DE SEO ────────────────────────────────────────────────
# Título e primeira linha da descrição SEMPRE começam com a palavra-chave
# principal por extenso. Nenhuma abreviação é aceita. Falha = bloqueio.
SEO_KEYWORD_BANK = Path(
    "/home/fvitorio/.config/opencode/skills/video-creator/keywords/banco_keywords.json"
)

CORE_SEO_KEYWORDS = [
    "landing page", "landing pages", "google ads", "tráfego pago",
    "marketing digital", "marketing", "captação de clientes", "conversão",
    "taxa de conversão", "lead", "leads", "google analytics", "ga4",
    "criativos", "segmentação", "copy", "funil",
]

# Termos de nicho também valem no início do título (padrão validado: nicho-primeiro)
NICHE_START_KEYWORDS = [
    "clínica", "clínicas", "advogado", "advogados", "advocacia",
    "contador", "contadores", "fisioterapia", "fisioterapeuta", "fisioterapeutas",
    "psicologia", "psicólogo", "psicólogos", "imobiliária", "imobiliárias",
    "estética", "esteticista", "esteticistas", "negócio local", "negócios locais",
    "marketing local", "google meu negócio", "agendamento", "marketing jurídico",
    "marketing médico", "marketing contábil", "tracking", "rastreamento",
    "google tag manager", "analytics", "mensuração",
]

# (regex, abreviação, forma correta)
ABBREVIATIONS_FORBIDDEN = [
    (r"\blps?\b", "LP/LPs", "landing page / landing pages"),
    (r"\bmkt\b", "MKT", "marketing"),
    (r"\bga\b", "GA", "Google Ads ou Google Analytics"),
    (r"\bconv\b", "CONV", "conversão"),
    (r"\bcap\.?\b", "CAP", "captação"),
    (r"\bcli\.?\b", "CLI", "cliente"),
    (r"\bpág\.?\b", "PÁG", "página"),
]


def _norm_text(text: str) -> str:
    """Lowercase + remove acentos preservando o comprimento do texto."""
    value = unicodedata.normalize("NFKD", text or "")
    value = "".join(c for c in value if not unicodedata.combining(c))
    return value.lower().strip()

# YouTube API scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
]

class YouTubeGrowthManager:
    def __init__(self):
        self.credentials = None
        self.youtube_service = None
        self.analytics_service = None
        self.history = self.load_history()
        
        # Ensure directories exist
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        if not GOOGLE_API_AVAILABLE:
            raise Exception("Google API libraries not available")
        
        creds = None
        
        # Load existing token
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            except Exception as e:
                print(f"Error loading token: {e}")
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = None
            if not creds:
                if not CLIENT_SECRETS_FILE.exists():
                    raise Exception(
                        f"Client secrets file not found: {CLIENT_SECRETS_FILE}\n"
                        "Please download OAuth 2.0 credentials from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CLIENT_SECRETS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.credentials = creds
        self.youtube_service = build('youtube', 'v3', credentials=creds)
        self.analytics_service = build('youtubeAnalytics', 'v2', credentials=creds)
        
        print("[YouTube] Authentication successful")
        return True
    
    def load_history(self) -> Dict:
        """Load upload history from JSON file"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load history file: {e}")
                return {}
        return {}
    
    def generate_utm_url(self, video_id: str, niche: str = "marketing") -> str:
        """
        Generate URL with UTM parameters for GA4 tracking
        
        Args:
            video_id: YouTube video ID
            niche: Content niche (clinicas, advogados, contadores, etc.)
            
        Returns:
            URL with UTM parameters
        """
        base_url = LANDING_URL
        utm_params = f"utm_source=youtube&utm_medium=shorts&utm_campaign={video_id}&utm_content={niche}"
        return f"{base_url}?{utm_params}"
    
    def add_utm_to_description(self, description: str, video_id: str, niche: str = "marketing") -> str:
        """
        Normaliza o link de conversão da descrição para a UTM do vídeo.
        
        Sempre reescreve a URL de diagnóstico (com ou sem query, com ou sem
        esquema) para a versão canônica com o video_id real — assim um .txt
        gravado com utm_campaign={stem} pelo video-creator é promovido para o
        utm_campaign={video_id} no upload, e um .txt sem UTM ganha uma.
        
        Args:
            description: Original description
            video_id: YouTube video ID
            niche: Content niche
            
        Returns:
            Description with UTM link
        """
        utm_url = self.generate_utm_url(video_id, niche)
        
        # Sempre reescreve (idempotente: mesma URL de entrada = mesma de saída)
        if _FVS7_LANDING_RE.search(description):
            return _FVS7_LANDING_RE.sub(utm_url, description)
        
        # Sem link de conversão: anexa o rastreável no fim
        return f"{description}\n\n👉 Diagnóstico Grátis: {utm_url}"
    
    def detect_niche_from_title(self, title: str) -> str:
        """
        Detect content niche from video title
        
        Args:
            title: Video title
            
        Returns:
            Niche slug for utm_content
        """
        title_lower = title.lower()
        
        niche_keywords = {
            "clinicas": ["clínica", "clínicas", "estética", "agendamento", "paciente"],
            "advogados": ["advogado", "advogados", "jurídico", "jurídica", "escritório"],
            "contadores": ["contador", "contadores", "contabilidade", "pj"],
            "fisioterapeutas": ["fisioterapeuta", "fisioterapia", "fisioterapeutas"],
            "psicologos": ["psicólogo", "psicólogos", "psicologia", "terapia"],
            "imobiliarias": ["imobiliária", "imobiliárias", "corretor", "imóvel"],
            "esteticistas": ["esteticista", "esteticistas", "estética"],
            "negocios_locais": ["negócio local", "negócios locais", "comércio", "região"],
            "landing_pages": ["landing page", "landing pages", "conversão", "cro"],
            "tracking": ["tracking", "conversão", "ga4", "gtm", "analytics"],
            "marketing": ["marketing", "google ads", "tráfego", "anúncio"]
        }
        
        for niche, keywords in niche_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return niche
        
        return "marketing"
    
    def save_history(self):
        """Save upload history to JSON file"""
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def find_video_files(self, video_name: Optional[str] = None) -> List[Tuple[Path, Path]]:
        """
        Find video and metadata file pairs in the video-maker directory
        
        Args:
            video_name: Optional specific name to search for (without extension)
            
        Returns:
            List of tuples (video_path, metadata_path)
        """
        pairs = []
        
        if video_name:
            # Search for specific video
            video_path = VIDEO_MAKER_DIR / f"{video_name}.mp4"
            metadata_path = VIDEO_MAKER_DIR / f"{video_name}.txt"
            if video_path.exists() and metadata_path.exists():
                pairs.append((video_path, metadata_path))
            else:
                print(f"[YouTube] Video pair not found for '{video_name}'")
                print(f"  Looking for: {video_path} and {metadata_path}")
        else:
            # Find all video-mp4 files and look for corresponding txt files
            for video_path in VIDEO_MAKER_DIR.glob("*.mp4"):
                metadata_path = VIDEO_MAKER_DIR / f"{video_path.stem}.txt"
                if metadata_path.exists():
                    pairs.append((video_path, metadata_path))
                else:
                    print(f"[YouTube] Warning: Metadata file not found for {video_path.name}")
        
        return pairs
    
    def parse_metadata_file(self, metadata_path: Path) -> Dict[str, str]:
        """
        Parse the metadata .txt file generated by video-creator
        
        Args:
            metadata_path: Path to the .txt file
            
        Returns:
            Dictionary with keys: title, description, hashtags
        """
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"Error reading metadata file {metadata_path}: {e}")
        
        # Extract title (allows optional blank lines before closing delimiter)
        title_pattern = (
            DELIMITER + '\n' +
            r'TÍTULO \(para YouTube Shorts / Reels / TikTok\)\n' +
            DELIMITER + '\n' +
            r'([\s\S]*?)\n\s*' +
            DELIMITER
        )
        title_match = re.search(title_pattern, content)
        title = title_match.group(1).strip() if title_match else ""
        
        # Extract description
        desc_pattern = (
            DELIMITER + '\n' +
            r'DESCRIÇÃO \(copie e cole\)\n' +
            DELIMITER + '\n' +
            r'([\s\S]*?)\n\s*' +
            DELIMITER
        )
        desc_match = re.search(desc_pattern, content)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract hashtags
        hashtags_pattern = (
            DELIMITER + '\n' +
            r'HASHTAGS \(para usar nos comentários ou descrição\)\n' +
            DELIMITER + '\n' +
            r'([\s\S]*?)\n\s*' +
            DELIMITER
        )
        hashtags_match = re.search(hashtags_pattern, content)
        hashtags_raw = hashtags_match.group(1).strip() if hashtags_match else ""
        # Clean up hashtags - extract just the tags
        if hashtags_raw:
            # Extract hashtags from lines that start with #
            hashtag_lines = [line.strip() for line in hashtags_raw.split('\n') if line.strip().startswith('#')]
            hashtags = ' '.join(hashtag_lines)
        else:
            hashtags = ""
        
        return {
            'title': title,
            'description': description,
            'hashtags': hashtags
        }

    def seo_keyword_list(self) -> List[str]:
        """Keyword bank (video-creator) + keywords centrais + termos de nicho."""
        keywords = list(CORE_SEO_KEYWORDS) + list(NICHE_START_KEYWORDS)
        try:
            bank = json.loads(SEO_KEYWORD_BANK.read_text(encoding='utf-8'))
            for niche in bank.values():
                for item in niche.get('keywords_principais', []):
                    keyword = (item.get('keyword') or '').strip()
                    if keyword:
                        keywords.append(keyword)
        except Exception as e:
            print(f"[YouTube] Warning: keyword bank not loaded ({e}), using core list only")
        return sorted({_norm_text(k) for k in keywords if k}, key=len, reverse=True)

    @staticmethod
    def _suggest_keyword_start(text: str, keywords: List[str]) -> str:
        """Monta sugestão movendo a keyword encontrada para o início do texto."""
        normalized = _norm_text(text)
        for keyword in keywords:
            position = normalized.find(keyword)
            if position >= 0:
                rest = (text[:position] + text[position + len(keyword):])
                rest = re.sub(r"\s+", " ", rest).strip(" :–-→|")
                original = text[position:position + len(keyword)]
                return f"{original}: {rest}" if rest else original
        return "Landing Page: ..."

    def seo_audit(self, title: str, description: str = "") -> List[str]:
        """
        REGRA INVIOLÁVEL de SEO:
        1. Título começa com a palavra-chave principal por extenso.
        2. Primeira linha da descrição idem.
        3. Nenhuma abreviação em título ou descrição.
        Retorna lista de erros (vazia = aprovado).
        """
        errors: List[str] = []
        keywords = self.seo_keyword_list()
        title_text = (title or "").strip()

        if not title_text:
            errors.append("Título vazio")
            return errors

        def check_start(text: str, label: str) -> None:
            first_line = text.strip().split("\n")[0].strip()
            if not first_line:
                errors.append(f"{label} vazio")
                return
            normalized = _norm_text(first_line)
            if not any(normalized.startswith(k) for k in keywords):
                errors.append(
                    f"{label} não começa com a palavra-chave por extenso: \"{first_line}\" "
                    f"→ sugestão: \"{self._suggest_keyword_start(first_line, keywords)}\""
                )

        def check_abbreviations(text: str, label: str) -> None:
            for pattern, abbr, correct in ABBREVIATIONS_FORBIDDEN:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    errors.append(
                        f"{label} contém a abreviação \"{match.group(0)}\" ({abbr}) "
                        f"→ escreva \"{correct}\""
                    )

        check_start(title_text, "Título")
        check_abbreviations(title_text, "Título")

        if description:
            check_start(description, "Descrição (primeira linha)")
            check_abbreviations(description, "Descrição")

        return errors

    def is_video_already_uploaded(self, video_path: Path) -> bool:
        """Check if a video has already been uploaded based on history"""
        video_stem = video_path.stem
        if video_stem in self.history:
            entry = self.history[video_stem]
            if entry.get('video_id') and entry.get('status') in ['uploaded', 'published', 'scheduled']:
                # Double-check with YouTube API if possible
                try:
                    if self.youtube_service:
                        response = self.youtube_service.videos().list(
                            part='status',
                            id=entry['video_id']
                        ).execute()
                        
                        if response.get('items'):
                            return True
                except Exception:
                    # If we can't verify, assume it's uploaded based on history
                    return True
        return False
    
    def upload_video(self, video_path: Path, metadata_path: Path, 
                     scheduled_time: Optional[datetime] = None,
                     force_duration: bool = False) -> Dict:
        """
        Upload a video to YouTube
        
        Args:
            video_path: Path to the .mp4 video file
            metadata_path: Path to the .txt metadata file
            scheduled_time: Optional datetime for scheduling the upload
            force_duration: Sobrepõe o gate de duração ≤30s (exceção documentada)
            
        Returns:
            Dictionary with upload results
        """
        # Authenticate if needed
        if not self.youtube_service:
            self.authenticate()
        
        # Check if already uploaded
        if self.is_video_already_uploaded(video_path):
            video_stem = video_path.stem
            existing_entry = self.history.get(video_stem, {})
            print(f"[YouTube] Video already uploaded: {video_stem}")
            print(f"  Video ID: {existing_entry.get('video_id')}")
            print(f"  Status: {existing_entry.get('status')}")
            return existing_entry
        
        # Parse metadata
        try:
            metadata = self.parse_metadata_file(metadata_path)
        except Exception as e:
            raise Exception(f"Failed to parse metadata: {e}")
        
        if not metadata['title']:
            raise Exception("No title found in metadata file")

        # REGRA INVIOLÁVEL: valida SEO antes de qualquer envio
        seo_errors = self.seo_audit(metadata['title'], metadata['description'])
        if seo_errors:
            details = "\n".join(f"  - {e}" for e in seo_errors)
            raise Exception(
                "[YouTube] SEO audit FAIL — publicação bloqueada (regra inviolável):\n"
                f"{details}\n"
                "  Action: corrija a seção TÍTULO/DESCRIÇÃO no arquivo .txt e rode "
                "`python3 youtube_growth.py seo-audit <arquivo.txt>` antes de repetir."
            )
        print("[YouTube] SEO audit PASS (keyword no início, sem abreviações)")

        # GATE DE DURAÇÃO — Shorts novos precisam de <= MAX_SHORT_DURATION_S
        duration = probe_duration_seconds(video_path)
        if duration is None:
            print("[YouTube] Aviso: ffprobe indisponível — duration gate ignorado "
                  f"({video_path.name})")
        elif duration > MAX_SHORT_DURATION_S:
            msg = (
                f"[YouTube] DURATION GATE FAIL — publicação bloqueada: "
                f"{video_path.name} tem {duration:.1f}s (máx. {MAX_SHORT_DURATION_S:.0f}s)\n"
                f"  Evidência: vídeos <=26s renderizam 34 views em média; "
                f"51-85s renderizam 11 (10 dias / 22 vídeos).\n"
                f"  Action: re-renderize o vídeo em <=30s com a video-creator, "
                f"ou use --force se esta for uma exceção documentada."
            )
            if not force_duration:
                raise Exception(msg)
            print(msg)
            print("[YouTube] --force recebido — seguindo apesar do gate.")
        else:
            print(f"[YouTube] Duration gate PASS ({duration:.1f}s <= "
                  f"{MAX_SHORT_DURATION_S:.0f}s)")

        # Detect niche and add UTM to description
        niche = self.detect_niche_from_title(metadata['title'])
        description_with_utm = self.add_utm_to_description(
            metadata['description'], 
            "TEMP_ID",  # Will be replaced after upload
            niche
        )
        
        # Prepare video metadata for YouTube
        body = {
            'snippet': {
                'title': metadata['title'],
                'description': description_with_utm,
                'tags': self._extract_tags_from_hashtags(metadata['hashtags']),
                'categoryId': '27'  # Education category - adjust as needed
            },
            'status': {
                'privacyStatus': 'private' if scheduled_time else 'private',  # Will change based on scheduling
                'selfDeclaredMadeForKids': False
            }
        }
        
        # If scheduling is requested, set the publish time
        if scheduled_time:
            # YouTube requires RFC 3339 format
            body['status']['publishAt'] = scheduled_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            body['status']['privacyStatus'] = 'private'  # Scheduled videos start as private
        
        print(f"[YouTube] Upload started: {metadata['title']}")
        if scheduled_time:
            print(f"[YouTube] Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Upload the video
        try:
            media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
            
            insert_request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            error = None
            retry = 0
            
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    if status:
                        print(f"[YouTube] Uploaded {int(status.progress() * 100)}%")
                except Exception as e:
                    if retry < 3:
                        retry += 1
                        print(f"[YouTube] Upload error, retrying ({retry}/3): {e}")
                        continue
                    else:
                        raise e
            
            if response is not None:
                video_id = response['id']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Generate final description with actual video_id
                final_description = self.add_utm_to_description(
                    metadata['description'],
                    video_id,
                    niche
                )
                
                # Update the video description with actual UTM
                try:
                    self.youtube_service.videos().update(
                        part='snippet',
                        body={
                            'id': video_id,
                            'snippet': {
                                'title': metadata['title'],
                                'description': final_description,
                                'tags': self._extract_tags_from_hashtags(metadata['hashtags']),
                                'categoryId': '27'
                            }
                        }
                    ).execute()
                except Exception as e:
                    print(f"[YouTube] Warning: Could not update description with UTM: {e}")
                
                # Update history
                video_stem = video_path.stem
                history_entry = {
                    'video_id': video_id,
                    'video_file': str(video_path),
                    'metadata_file': str(metadata_path),
                    'title': metadata['title'],
                    'description': final_description,
                    'hashtags': metadata['hashtags'],
                    'youtube_url': video_url,
                    'uploaded_at': datetime.now().isoformat(),
                    'scheduled_at': scheduled_time.isoformat() if scheduled_time else None,
                    'published_at': None,
                    'status': 'scheduled' if scheduled_time else 'uploaded',
                    'privacy_status': body['status']['privacyStatus']
                }
                
                self.history[video_stem] = history_entry
                self.save_history()
                
                print(f"[YouTube] Upload completed")
                print(f"[YouTube] Video ID: {video_id}")
                print(f"[YouTube] URL: {video_url}")
                
                if scheduled_time:
                    print(f"[YouTube] Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                
                return history_entry
            
        except Exception as e:
            print(f"[YouTube] Upload failed: {e}")
            raise
    
    def _extract_tags_from_hashtags(self, hashtags_str: str) -> List[str]:
        """Extract tags from hashtags string for YouTube upload"""
        if not hashtags_str:
            return []
        
        # Extract words that start with # and remove the #
        tags = []
        for word in hashtags_str.split():
            if word.startswith('#'):
                tag = word[1:]  # Remove the #
                # YouTube tags have restrictions: max 30 chars, no commas, etc.
                if len(tag) <= 30 and ',' not in tag:
                    tags.append(tag)
        
        # Limit to reasonable number of tags (YouTube allows up to 500 characters total)
        return tags[:10]  # Conservative limit
    
    def list_scheduled_videos(self) -> List[Dict]:
        """List all scheduled videos from history"""
        scheduled = []
        for video_stem, entry in self.history.items():
            if entry.get('status') == 'scheduled' and entry.get('scheduled_at'):
                scheduled.append(entry)
        
        # Sort by scheduled time
        scheduled.sort(key=lambda x: x.get('scheduled_at', ''))
        return scheduled
    
    def get_video_status(self, video_id: str) -> Dict:
        """Get current status of a video from YouTube API"""
        if not self.youtube_service:
            self.authenticate()
        
        try:
            response = self.youtube_service.videos().list(
                part='status,snippet',
                id=video_id
            ).execute()
            
            if response.get('items'):
                item = response['items'][0]
                return {
                    'video_id': video_id,
                    'title': item['snippet'].get('title'),
                    'description': item['snippet'].get('description'),
                    'tags': item['snippet'].get('tags', []),
                    'privacy_status': item['status'].get('privacyStatus'),
                    'publish_at': item['status'].get('publishAt'),
                    'uploaded_at': item['snippet'].get('publishedAt')
                }
            else:
                return {'error': 'Video not found'}
        except Exception as e:
            return {'error': str(e)}
    
    def cancel_scheduled_video(self, video_id: str) -> bool:
        """Cancel a scheduled video by changing its privacy status back to private"""
        if not self.youtube_service:
            self.authenticate()
        
        try:
            # First get current video details
            video_info = self.get_video_status(video_id)
            if 'error' in video_info:
                print(f"[YouTube] Error getting video info: {video_info['error']}")
                return False
            
            # Update the video to remove scheduled time and set to private
            update_body = {
                'id': video_id,
                'snippet': {
                    'title': video_info['title'],
                    'description': video_info['description'],
                    'tags': video_info.get('tags', []),
                    'categoryId': '27'
                },
                'status': {
                    'privacyStatus': 'private',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Remove publishAt field to cancel scheduling
            if 'publishAt' in update_body['status']:
                del update_body['status']['publishAt']
            
            self.youtube_service.videos().update(
                part='snippet,status',
                body=update_body
            ).execute()
            
            # Update history
            for video_stem, entry in self.history.items():
                if entry.get('video_id') == video_id:
                    entry['status'] = 'uploaded'  # Back to uploaded but not scheduled
                    entry['scheduled_at'] = None
                    entry['privacy_status'] = 'private'
                    break
            
            self.save_history()
            print(f"[YouTube] Scheduled publication cancelled for video {video_id}")
            return True
            
        except Exception as e:
            print(f"[YouTube] Error cancelling scheduled video: {e}")
            return False
    
    def publish_now(self, video_id: str) -> bool:
        """Publish a scheduled video immediately"""
        if not self.youtube_service:
            self.authenticate()
        
        try:
            # Get current video details
            video_info = self.get_video_status(video_id)
            if 'error' in video_info:
                print(f"[YouTube] Error getting video info: {video_info['error']}")
                return False
            
            # Update the video to public (immediate publish)
            update_body = {
                'id': video_id,
                'snippet': {
                    'title': video_info['title'],
                    'description': video_info['description'],
                    'tags': video_info.get('tags', []),
                    'categoryId': '27'
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False,
                }
            }
            
            self.youtube_service.videos().update(
                part='snippet,status',
                body=update_body
            ).execute()
            
            # Update history
            stem = None
            for video_stem, entry in self.history.items():
                if entry.get('video_id') == video_id:
                    entry['status'] = 'published'
                    entry['published_at'] = datetime.now().isoformat()
                    entry['privacy_status'] = 'public'
                    stem = video_stem
                    break
            
            self.save_history()
            print(f"[YouTube] Video {video_id} published immediately")

            # Comentário com CTA: só faz sentido quando o vídeo está público
            if stem and not self.history[stem].get('comment_id'):
                self.comment_video(stem)
            return True
            
        except Exception as e:
            import traceback
            print(f"[YouTube] Error publishing video immediately: {e}")
            print(f"[YouTube] Exception type: {type(e)}")
            traceback.print_exc()
            return False

    def schedule_existing_publish(self, video_id: str, scheduled_time: datetime) -> bool:
        """
        Schedule an already-uploaded (private) video to be published at a future time.
        Sets privacyStatus=private + publishAt so YouTube publishes it automatically.

        Args:
            video_id: YouTube video ID (must already exist / be uploaded)
            scheduled_time: datetime when the video should go public

        Returns:
            True on success, False otherwise
        """
        if not self.youtube_service:
            self.authenticate()

        if scheduled_time <= datetime.now():
            print(f"[YouTube] Scheduled time is in the past: {scheduled_time}")
            return False

        try:
            # Get current video details (title/description/tags preserved)
            video_info = self.get_video_status(video_id)
            if 'error' in video_info:
                print(f"[YouTube] Error getting video info: {video_info['error']}")
                return False

            seo_errors = self.seo_audit(
                video_info['title'], video_info.get('description') or ''
            )
            if seo_errors:
                print(f"[SEO] BLOQUEADO: vídeo {video_id} não passa na auditoria de SEO.")
                for err in seo_errors:
                    print(f"[SEO]   - {err}")
                print(f"[SEO] Corrija antes de agendar: "
                      f"python3 youtube_growth.py seo-audit {video_id}")
                return False

            # Update the video to scheduled (private until publishAt)
            update_body = {
                'id': video_id,
                'snippet': {
                    'title': video_info['title'],
                    'description': video_info['description'],
                    'tags': video_info.get('tags', []),
                    'categoryId': '27'
                },
                'status': {
                    'privacyStatus': 'private',
                    'selfDeclaredMadeForKids': False,
                    'publishAt': scheduled_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                }
            }

            self.youtube_service.videos().update(
                part='snippet,status',
                body=update_body
            ).execute()

            # Update history
            for video_stem, entry in self.history.items():
                if entry.get('video_id') == video_id:
                    entry['status'] = 'scheduled'
                    entry['scheduled_at'] = scheduled_time.isoformat()
                    entry['published_at'] = None
                    entry['privacy_status'] = 'private'
                    break

            self.save_history()
            print(f"[YouTube] Video {video_id} scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            return True

        except Exception as e:
            import traceback
            print(f"[YouTube] Error scheduling video: {e}")
            print(f"[YouTube] Exception type: {type(e)}")
            traceback.print_exc()
            return False

    def update_metadata(self, video_id: str, title: str, description: str, add_utm: bool = True) -> bool:
        """
        Update an existing video's title and description, preserving its current
        privacy status and schedule (publishAt) so scheduled videos stay scheduled
        and published videos stay public.

        Args:
            video_id: YouTube video ID
            title: New video title
            description: New video description
            add_utm: Whether to add UTM parameters to links (default: True)

        Returns:
            True on success, False otherwise
        """
        if not self.youtube_service:
            self.authenticate()

        # REGRA INVIOLÁVEL: valida SEO antes de atualizar metadados
        seo_errors = self.seo_audit(title, description)
        if seo_errors:
            print(f"[YouTube] SEO audit FAIL — atualização bloqueada (regra inviolável):")
            for error in seo_errors:
                print(f"  - {error}")
            return False

        try:
            video_info = self.get_video_status(video_id)
            if 'error' in video_info:
                print(f"[YouTube] Error getting video info: {video_info['error']}")
                return False

            # Add UTM to description if requested
            if add_utm:
                niche = self.detect_niche_from_title(title)
                description = self.add_utm_to_description(description, video_id, niche)

            # Preserve current privacy status + schedule
            status = {
                'privacyStatus': video_info.get('privacy_status', 'private'),
                'selfDeclaredMadeForKids': False,
            }
            if video_info.get('publish_at'):
                status['publishAt'] = video_info['publish_at']

            update_body = {
                'id': video_id,
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': video_info.get('tags', []),
                    'categoryId': '27'
                },
                'status': status
            }

            self.youtube_service.videos().update(
                part='snippet,status',
                body=update_body
            ).execute()

            # Update history
            for video_stem, entry in self.history.items():
                if entry.get('video_id') == video_id:
                    entry['title'] = title
                    entry['description'] = description
                    break

            self.save_history()
            print(f"[YouTube] Updated metadata for {video_id}: {title}")
            return True

        except Exception as e:
            import traceback
            print(f"[YouTube] Error updating metadata for {video_id}: {e}")
            print(f"[YouTube] Exception type: {type(e)}")
            traceback.print_exc()
            return False

    def add_comment(self, video_id: str, text: str) -> Optional[str]:
        """
        Add a comment to a YouTube video.

        Args:
            video_id: YouTube video ID
            text: Comment text (max 1000 chars)

        Returns:
            comment_id on success, None otherwise
        """
        if not self.youtube_service:
            self.authenticate()

        try:
            # Truncate if too long
            if len(text) > 1000:
                text = text[:997] + "..."

            comment_body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": text
                        }
                    }
                }
            }

            response = self.youtube_service.commentThreads().insert(
                part="snippet",
                body=comment_body
            ).execute()

            print(f"[YouTube] Comment added to {video_id}")
            return response.get('id')

        except Exception as e:
            print(f"[YouTube] Error adding comment to {video_id}: {e}")
            return None

    def build_pinned_comment(self, title: str, video_id: str,
                             niche: str = "marketing") -> str:
        """
        Texto do comentário com CTA + link rastreável (template da video-creator).

        A API do YouTube não fixa (pin) comentários — fixe manualmente no Studio.
        """
        url = self.generate_utm_url(video_id, niche)
        blocks = [
            f"🎯 {title} — o que está travando o seu resultado?",
            f"👉 Diagnóstico grátis em 15 minutos: {url}",
            "📊 +150 projetos entregues | 4.9/5 avaliação dos clientes",
            "Qual desses pontos mais se parece com a sua situação? Comenta aqui 👇",
        ]
        text = blocks[0]
        for block in blocks[1:]:
            candidate = f"{text}\n{block}"
            if len(candidate) > 997:
                break
            text = candidate
        return text

    def comment_video(self, target: str) -> Optional[str]:
        """
        Adiciona o comentário com CTA num vídeo já publicado.

        target: stem do vídeo, video_id ou caminho .txt.
        Idempotente: se já existe comentário registrado, não duplica.
        Retorna o comment_id ou None.
        """
        if not self.youtube_service:
            self.authenticate()

        stem, entry = None, None
        if target in self.history and isinstance(self.history[target], dict):
            stem, entry = target, self.history[target]
        else:
            found = self._find_entry(target)
            if not found:
                print(f"[YouTube] Comentário: vídeo não encontrado para '{target}'")
                return None
            stem, entry = found

        video_id = entry.get('video_id')
        if not video_id:
            print(f"[YouTube] Comentário: '{stem}' não tem video_id")
            return None
        if entry.get('comment_id'):
            print(f"[YouTube] Comentário já existe em {video_id} "
                  f"({entry['comment_id']}) — nada a fazer")
            return entry['comment_id']

        niche = self.detect_niche_from_title(entry.get('title') or '')
        text = self.build_pinned_comment(entry.get('title') or '', video_id, niche)
        comment_id = self.add_comment(video_id, text)
        if comment_id:
            entry['comment_id'] = comment_id
            entry['commented_at'] = datetime.now().isoformat(timespec='seconds')
            self.save_history()
            print(f"[YouTube] Comentário registrado em {video_id}: {comment_id}")
            print("  A API não fixa comentário — fixe no YouTube Studio se quiser")
        return comment_id

    # ── TikTok (pacote semi-manual) ────────────────────────────────────────

    # Qualquer URL do domínio sai da legenda: TikTok não formata como link.
    _FVS7_ANY_URL_RE = re.compile(
        r'(?<![\w.-])(?:(?:https?://)?(?:www\.)?)?fvs7\.com\.br(?:/[^\s]*)?'
    )
    # Linhas que só serviam de suporte ao link e ficam órfãs depois da remoção.
    _ORPHAN_CTA_LINE_RE = re.compile(
        r'^\s*(?:👉|📞|🌐|🔗|💥|🔥|⬇|📍|🎯)?\s*'
        r'(?:diagn[oó]stico(?:\s+gr[aá]tis)?(?:\s+em\s+\d+\s+minutos?)?'
        r'|acesse(?:\s+agora)?|fale\s+conosco|saiba\s+mais|agende'
        r'|link(?:\s+na\s+bio)?)\s*:?\s*$',
        re.IGNORECASE,
    )

    def build_tiktok_caption(self, metadata: Dict[str, str],
                             slug: str = "") -> str:
        """
        Monta a legenda do TikTok.

        - keyword na 1ª linha (regra inviolável de SEO)
        - fonte da descrição: history.json quando existe (descrição já
          reescrita/otimizada), senão o .txt cru da video-creator
        - TODA URL sai do corpo (TikTok não clica em legenda/comentário) e vira
          um CTA duplo: "link na bio" (único clique real) + URL com UTM
          rastreável para quem copiar/colar
        - hashtags no fim, corte em TIKTOK_CAPTION_LIMIT preservando o início
        """
        slug = (slug or '').strip()
        hashtags = (metadata.get('hashtags') or '').strip()

        # 1) fonte da descrição: histórico (preferido) > .txt
        description = (metadata.get('description') or '').strip()
        entry = self.history.get(slug) if slug else None
        if isinstance(entry, dict) and (entry.get('description') or '').strip():
            description = entry['description'].strip()

        # 2) remove a linha de hashtags solta da descrição (já vem em hashtags)
        body_lines = [
            line for line in description.split('\n')
            if not re.fullmatch(r'\s*#\S+(?:\s+#\S+)*\s*', line)
        ]
        body = '\n'.join(body_lines).strip()

        # 3) remove URLs do domínio e as linhas que sobram vazias sem sentido
        body = self._FVS7_ANY_URL_RE.sub('', body)
        body = '\n'.join(
            line for line in body.split('\n')
            if not self._ORPHAN_CTA_LINE_RE.match(line)
        )
        body = re.sub(r'[ \t]+\n', '\n', body)
        body = re.sub(r'\n{3,}', '\n\n', body).strip()
        body = re.sub(r'\s+:$', '', body).strip()
        if not body:
            body = (metadata.get('title') or '').strip()

        # 4) CTA duplo — bio clicável + URL para copiar/colar (com UTM)
        copy_url = tiktok_utm_url(slug)
        cta = (
            "🔗 Diagnóstico grátis — link na bio\n"
            f"🌐 Copie e cole: {copy_url}"
        )

        def join(parts: List[str]) -> str:
            return '\n\n'.join(p for p in parts if p)

        caption = join([body, cta, hashtags])
        if len(caption) > TIKTOK_CAPTION_LIMIT:
            # reserva CTA + hashtags: o corte só pode comer o miolo do texto
            reserved = len(cta) + len(hashtags) + 4
            body = body[:max(0, TIKTOK_CAPTION_LIMIT - reserved)].rstrip()
            caption = join([body, cta, hashtags])
        return caption

    @staticmethod
    def _copy_to_clipboard(text: str) -> bool:
        """Copia texto para a área de transferência (best-effort)."""
        candidates = []
        if shutil.which('wl-copy'):
            candidates.append(['wl-copy'])
        if shutil.which('xclip'):
            candidates.append(['xclip', '-selection', 'clipboard'])
        if shutil.which('xsel'):
            candidates.append(['xsel', '--clipboard', '--input'])
        if shutil.which('xclip') is None and shutil.which('wl-copy') is None \
                and shutil.which('xsel') is None and sys.platform == 'darwin':
            candidates.append(['pbcopy'])
        for cmd in candidates:
            try:
                subprocess.run(cmd, input=text.encode('utf-8'), check=True,
                               capture_output=True, timeout=10)
                return True
            except Exception:
                continue
        return False

    def tiktok_package(self, video_path: Path, metadata_path: Path) -> Dict:
        """
        Gera o pacote de publicação manual no TikTok.

        READ + arquivo local: não publica nada. A regra inviolável de SEO roda
        antes de gerar qualquer arquivo — falhou, não existe pacote.
        """
        metadata = self.parse_metadata_file(metadata_path)
        caption = self.build_tiktok_caption(metadata, slug=video_path.stem)

        seo_errors = self.seo_audit(metadata['title'], caption)
        if seo_errors:
            print("[YouTube] TikTok package BLOCKED (regra inviolável de SEO):")
            for error in seo_errors:
                print(f"  - {error}")
            print("  Action: corrija o .txt da video-creator e rode de novo")
            raise Exception("SEO audit falhou — pacote não gerado")

        caption_path = TIKTOK_DIR / f"{video_path.stem}.tiktok.txt"
        caption_path.write_text(caption + "\n", encoding='utf-8')

        copied = self._copy_to_clipboard(caption)

        duration = probe_duration_seconds(video_path)
        now = datetime.now().isoformat(timespec='seconds')

        entry = self.history.setdefault(video_path.stem, {})
        entry.setdefault('title', metadata['title'])
        entry.setdefault('description', metadata['description'])
        entry.setdefault('hashtags', metadata['hashtags'])
        entry.setdefault('video_file', str(video_path))
        entry.setdefault('metadata_file', str(metadata_path))
        if duration:
            entry.setdefault('duration', duration)
        # Preserva o que já existe (idempotência): um pacote manual não pode
        # apagar um agendamento/publicação ativo no Buffer.
        existing = entry.get('tiktok') if isinstance(entry.get('tiktok'), dict) else {}
        tiktok_state = {**existing}
        if tiktok_state.get('status') not in ('scheduled', 'published'):
            tiktok_state['status'] = 'prepared'
        tiktok_state.update({
            'caption_file': str(caption_path),
            'caption_chars': len(caption),
            'copy_url': tiktok_utm_url(video_path.stem),
            'bio_url': TIKTOK_BIO_URL,
            'video_file': str(video_path),
            'prepared_at': now,
        })
        entry['tiktok'] = tiktok_state
        self.save_history()

        print("[YouTube] TikTok package prepared (publicação manual)")
        print(f"  Vídeo: {video_path}")
        print(f"  Legenda: {caption_path} ({len(caption)}/{TIKTOK_CAPTION_LIMIT} chars)")
        print(f"  1ª linha: {caption.splitlines()[0] if caption else ''}")
        print(f"  Link clicável do TikTok (bio, 1 só): {TIKTOK_BIO_URL}")
        print(f"  URL de cópia da legenda (rastreável): {tiktok_utm_url(video_path.stem)}")
        print(f"  Área de transferência: {'copiada' if copied else 'indisponível (copie do arquivo)'}")
        print("  Próximo passo: abra o TikTok, cole a legenda e selecione o vídeo")
        return {'caption_file': str(caption_path), 'caption': caption,
                'bio_url': TIKTOK_BIO_URL,
                'copy_url': tiktok_utm_url(video_path.stem),
                'copied': copied, 'duration': duration}

    def _find_entry(self, target: str) -> Optional[Tuple[str, Dict]]:
        """Localiza a entrada do histórico por nome, video_id ou caminho .txt."""
        if target in self.history and isinstance(self.history[target], dict):
            return target, self.history[target]

        path = Path(target).expanduser()
        if path.suffix in ('.txt', '.mp4') and path.exists():
            stem = path.stem.replace('.tiktok', '')
            if stem in self.history and isinstance(self.history[stem], dict):
                return stem, self.history[stem]

        pairs = self.find_video_files(Path(target).stem)
        if pairs:
            stem = pairs[0][0].stem
            if stem in self.history and isinstance(self.history[stem], dict):
                return stem, self.history[stem]

        for key, value in self.history.items():
            if isinstance(value, dict) and value.get('video_id') == target:
                return key, value
        return None

    def _find_tiktok_entry(self, target: str) -> Optional[Tuple[str, Dict]]:
        """Localiza a entrada do histórico (alias usado pelos comandos TikTok)."""
        return self._find_entry(target)

    def tiktok_mark_published(self, target: str) -> bool:
        """Registra que o vídeo foi publicado manualmente no TikTok."""
        found = self._find_tiktok_entry(target)
        if not found:
            print(f"[YouTube] TikTok: entrada não encontrada para '{target}'")
            return False
        stem, entry = found
        tiktok = entry.setdefault('tiktok', {})
        tiktok['status'] = 'published'
        tiktok['published_at'] = datetime.now().isoformat(timespec='seconds')
        self.save_history()
        print(f"[YouTube] TikTok: '{stem}' marcado como publicado")
        print("  Confirme a publicação no seu perfil do TikTok")
        return True

    def tiktok_list(self) -> List[Dict]:
        """Lista o estado dos pacotes TikTok registrados localmente."""
        items = []
        for stem, entry in self.history.items():
            if not isinstance(entry, dict):
                continue
            tiktok = entry.get('tiktok')
            if not isinstance(tiktok, dict):
                continue
            items.append({
                'stem': stem,
                'title': entry.get('title', ''),
                'status': tiktok.get('status', 'unknown'),
                'caption_file': tiktok.get('caption_file', ''),
                'prepared_at': tiktok.get('prepared_at', ''),
                'scheduled_at': tiktok.get('scheduled_at', ''),
                'published_at': tiktok.get('published_at', ''),
                'buffer_post_id': tiktok.get('buffer_post_id', ''),
            })
        items.sort(key=lambda item: item.get('prepared_at') or '')
        return items

    def tiktok_caption_sync(self, execute: bool = False) -> Dict:
        """
        Reescreve a legenda dos posts JÁ agendados no Buffer usando o
        history.json (fonte mais nova, com a descrição reescrita pela Ação 5).

        O Buffer guarda o texto no momento do agendamento, então os posts
        criados antes da mudança continuam com a legenda antiga (sem CTA de bio).
        `editPost` atualiza só o texto — horário e vídeo ficam intactos.

        Dry-run por padrão: execute=False só lista. execute=True aplica.
        """
        results = {'updated': [], 'same': [], 'skipped': [], 'missing': []}
        if not any(isinstance(e, dict) and isinstance(e.get('tiktok'), dict)
                   and e['tiktok'].get('buffer_post_id')
                   for e in self.history.values()):
            return results

        remote = {n['id']: n for n in self.buffer_scheduled_posts()}

        for stem, entry in sorted(self.history.items()):
            if not isinstance(entry, dict):
                continue
            tiktok = entry.get('tiktok')
            if not isinstance(tiktok, dict):
                continue
            post_id = tiktok.get('buffer_post_id')
            if tiktok.get('status') != 'scheduled' or not post_id:
                continue
            if post_id not in remote:
                results['missing'].append((stem, post_id))
                continue

            metadata = {
                'title': entry.get('title', ''),
                'description': entry.get('description', ''),
                'hashtags': entry.get('hashtags', ''),
            }
            if not metadata['title'] or not metadata['description']:
                results['skipped'].append((stem, 'sem title/description no history'))
                continue

            caption = self.build_tiktok_caption(metadata, slug=stem)
            seo_errors = self.seo_audit(metadata['title'], caption)
            if seo_errors:
                results['skipped'].append((stem, f'bloqueado por SEO: {seo_errors[0]}'))
                continue

            current = remote[post_id].get('text') or ''
            if current.strip() == caption.strip():
                results['same'].append(stem)
                continue

            if not execute:
                results['updated'].append((stem, post_id))
                continue
            try:
                video_url = (tiktok.get('video_url')
                             or (remote[post_id].get('assets') or [{}])[0].get('source'))
                if not video_url:
                    raise Exception("sem video_url no history nem asset no Buffer")
                self.buffer_edit_post_text(post_id, caption, video_url)
                tiktok['caption_chars'] = len(caption)
                tiktok['caption_synced_at'] = datetime.now().isoformat(timespec='seconds')
                results['updated'].append((stem, post_id))
                print(f"[YouTube] Buffer: legenda atualizada ({stem}) "
                      f"{len(current)} → {len(caption)} chars")
            except Exception as e:
                results['skipped'].append((stem, f'erro Buffer: {str(e)[:120]}'))

        if execute:
            self.save_history()
        return results

    # ── Buffer + Cloudinary (agendamento automático no TikTok) ─────────────

    @staticmethod
    def _load_credential(filename: str) -> Dict:
        path = CREDENTIALS_DIR / filename
        if not path.exists():
            raise Exception(
                f"Credencial ausente: {path}\n"
                f"  Action: crie o arquivo JSON com as credenciais"
            )
        return json.loads(path.read_text(encoding='utf-8'))

    def cloudinary_upload_video(self, video_path: Path) -> str:
        """Sobe o vídeo para o Cloudinary e devolve a URL pública (HTTPS)."""
        try:
            import requests
        except ImportError:
            raise Exception("requests não instalado (pip install requests)")

        cfg = self._load_credential('cloudinary.json')
        params = {
            'timestamp': int(datetime.now().timestamp()),
            'folder': TIKTOK_HOST_FOLDER,
            'public_id': video_path.stem,
            'overwrite': 'true',
        }
        to_sign = '&'.join(f'{k}={params[k]}' for k in sorted(params)) + cfg['api_secret']
        params['signature'] = hashlib.sha1(to_sign.encode('utf-8')).hexdigest()
        params['api_key'] = cfg['api_key']

        print(f"[YouTube] Cloudinary upload: {video_path.name}")
        with open(video_path, 'rb') as handle:
            response = requests.post(
                f"https://api.cloudinary.com/v1_1/{cfg['cloud_name']}/video/upload",
                data=params, files={'file': handle}, timeout=600,
            )
        if response.status_code != 200:
            raise Exception(f"Cloudinary upload falhou ({response.status_code}): "
                            f"{response.text[:300]}")
        url = response.json().get('secure_url')
        if not url:
            raise Exception("Cloudinary não devolveu secure_url")

        head = requests.head(url, timeout=30)
        if head.status_code != 200:
            raise Exception(f"URL do Cloudinary não é pública: {url} ({head.status_code})")
        print(f"[YouTube] Vídeo público: {url}")
        return url

    def buffer_create_tiktok_post(self, caption: str, video_url: str,
                                  due_at: datetime) -> Dict:
        """Cria o post agendado no canal TikTok do Buffer (publicação automática)."""
        try:
            import requests
        except ImportError:
            raise Exception("requests não instalado (pip install requests)")

        buf = self._load_credential('buffer.json')
        headers = {'Content-Type': 'application/json',
                   'Authorization': f"Bearer {buf['token']}"}
        due_utc = due_at.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        variables = {'input': {
            'text': caption,
            'channelId': buf['tiktok_channel_id'],
            'schedulingType': 'automatic',
            'mode': 'customScheduled',
            'dueAt': due_utc,
            'assets': [{'video': {'url': video_url,
                                  'metadata': {'thumbnailOffset': 2000}}}],
        }}
        query = '''
        mutation Create($input: CreatePostInput!) {
          createPost(input: $input) {
            ... on PostActionSuccess { post { id status shareMode schedulingType dueAt } }
            ... on MutationError { message }
            ... on InvalidInputError { message }
            ... on LimitReachedError { message }
            ... on UnauthorizedError { message }
          }
        }'''
        response = requests.post('https://api.buffer.com', headers=headers,
                                 json={'query': query, 'variables': variables},
                                 timeout=60)
        data = response.json()
        if data.get('errors'):
            raise Exception(f"Buffer API: {data['errors'][0].get('message')}")
        result = data.get('data', {}).get('createPost') or {}
        post = result.get('post')
        if not post:
            raise Exception(f"Buffer não criou o post: {json.dumps(result, ensure_ascii=False)}")
        print(f"[YouTube] Buffer: post {post['id']} status={post['status']} "
              f"scheduling={post.get('schedulingType')}")
        return post

    def buffer_delete_post(self, post_id: str) -> bool:
        """Remove um post do Buffer (agendado ou rascunho)."""
        try:
            import requests
        except ImportError:
            raise Exception("requests não instalado (pip install requests)")

        buf = self._load_credential('buffer.json')
        headers = {'Content-Type': 'application/json',
                   'Authorization': f"Bearer {buf['token']}"}
        query = '''
        mutation Del($id: PostId!) {
          deletePost(input: {id: $id}) {
            __typename
            ... on MutationError { message }
            ... on VoidMutationError { message }
          }
        }'''
        response = requests.post('https://api.buffer.com', headers=headers,
                                 json={'query': query, 'variables': {'id': post_id}},
                                 timeout=60)
        data = response.json()
        if data.get('errors'):
            raise Exception(f"Buffer API: {data['errors'][0].get('message')}")
        typename = (data.get('data', {}).get('deletePost') or {}).get('__typename')
        if typename != 'DeletePostSuccess':
            raise Exception(f"Buffer não apagou o post {post_id}: {data}")
        return True

    def buffer_edit_post_text(self, post_id: str, text: str,
                              video_url: Optional[str] = None) -> bool:
        """
        Atualiza o texto de um post já agendado no Buffer (editPost).

        O Buffer REVALIDA o post inteiro no edit: sem `assets` ele responde
        "TikTok posts require at least one image or video". Então o vídeo é
        reenviado junto (mesma URL que já estava no post).
        """
        try:
            import requests
        except ImportError:
            raise Exception("requests não instalado (pip install requests)")

        buf = self._load_credential('buffer.json')
        headers = {'Content-Type': 'application/json',
                   'Authorization': f"Bearer {buf['token']}"}
        variables: Dict = {'input': {'id': post_id, 'text': text}}
        if video_url:
            variables['input']['assets'] = [
                {'video': {'url': video_url,
                           'metadata': {'thumbnailOffset': 2000}}}
            ]
        query = '''
        mutation Edit($input: EditPostInput!) {
          editPost(input: $input) {
            ... on PostActionSuccess { post { id status text dueAt } }
            ... on MutationError { message }
            ... on InvalidInputError { message }
            ... on UnauthorizedError { message }
          }
        }'''
        response = requests.post('https://api.buffer.com', headers=headers,
                                 json={'query': query, 'variables': variables},
                                 timeout=60)
        data = response.json()
        if data.get('errors'):
            raise Exception(f"Buffer API: {data['errors'][0].get('message')}")
        result = data.get('data', {}).get('editPost') or {}
        if not result.get('post'):
            raise Exception(f"Buffer não editou o post {post_id}: "
                            f"{json.dumps(result, ensure_ascii=False)}")
        return True

    def tiktok_buffer(self, video_path: Path, metadata_path: Path,
                      scheduled_time: datetime, force: bool = False) -> Dict:
        """
        Agenda publicação automática no TikTok via Buffer (PUBLISH).

        Ordem: regra de SEO → upload no Cloudinary → createPost no Buffer →
        registro no histórico. Qualquer falha = nada agendado.
        """
        metadata = self.parse_metadata_file(metadata_path)
        caption = self.build_tiktok_caption(metadata, slug=video_path.stem)

        seo_errors = self.seo_audit(metadata['title'], caption)
        if seo_errors:
            print("[YouTube] TikTok/Buffer BLOCKED (regra inviolável de SEO):")
            for error in seo_errors:
                print(f"  - {error}")
            print("  Action: corrija o .txt da video-creator e rode de novo")
            raise Exception("SEO audit falhou — nada enviado ao Buffer")

        stem = video_path.stem
        entry = self.history.get(stem) if isinstance(self.history.get(stem), dict) else {}
        existing = entry.get('tiktok') if isinstance(entry.get('tiktok'), dict) else {}
        if not force and existing.get('status') == 'scheduled' \
                and existing.get('buffer_post_id'):
            raise Exception(
                f"'{stem}' já está agendado no Buffer (post {existing['buffer_post_id']}, "
                f"{existing.get('scheduled_at')}). Use tiktok-buffer-cancel antes ou --force"
            )

        from zoneinfo import ZoneInfo
        local_tz = ZoneInfo('America/Sao_Paulo')
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=local_tz)
        if scheduled_time <= datetime.now(local_tz):
            raise Exception(f"Horário no passado: {scheduled_time}")

        duration = probe_duration_seconds(video_path)
        video_url = self.cloudinary_upload_video(video_path)
        post = self.buffer_create_tiktok_post(caption, video_url, scheduled_time)

        entry = self.history.setdefault(stem, {})
        entry.setdefault('title', metadata['title'])
        entry.setdefault('description', metadata['description'])
        entry.setdefault('hashtags', metadata['hashtags'])
        entry.setdefault('video_file', str(video_path))
        entry.setdefault('metadata_file', str(metadata_path))
        if duration:
            entry.setdefault('duration', duration)
        entry['tiktok'] = {
            **{k: v for k, v in existing.items() if k != 'buffer_post_id'},
            'status': 'scheduled',
            'buffer_post_id': post['id'],
            'video_url': video_url,
            'caption_chars': len(caption),
            'copy_url': tiktok_utm_url(stem),
            'bio_url': TIKTOK_BIO_URL,
            'scheduled_at': scheduled_time.isoformat(timespec='seconds'),
            'buffer_due_at': post.get('dueAt', ''),
            'updated_at': datetime.now().isoformat(timespec='seconds'),
        }
        self.save_history()

        print("[YouTube] TikTok agendado no Buffer (publicação automática)")
        print(f"  Vídeo: {video_path}")
        print(f"  Post Buffer: {post['id']} ({post.get('schedulingType')})")
        print(f"  Publica em: {scheduled_time.strftime('%A, %d/%m/%Y %H:%M')} "
              f"America/Sao_Paulo")
        print("  Confirme no Buffer antes do horário — o TikTok pode pedir "
              "aprovação no app se a conta não publicar direto")
        return {'post_id': post['id'], 'video_url': video_url,
                'scheduled_at': scheduled_time.isoformat()}

    def tiktok_buffer_cancel(self, target: str, force: bool = False) -> bool:
        """Cancela o agendamento do Buffer e volta o status para 'prepared'."""
        found = self._find_tiktok_entry(target)
        if not found:
            print(f"[YouTube] TikTok: entrada não encontrada para '{target}'")
            return False
        stem, entry = found
        tiktok = entry.get('tiktok') or {}
        post_id = tiktok.get('buffer_post_id')
        if not post_id:
            print(f"[YouTube] TikTok: '{stem}' não tem agendamento no Buffer")
            return False

        self.buffer_delete_post(post_id)
        tiktok['status'] = 'prepared'
        tiktok['cancelled_post_id'] = post_id
        if tiktok.get('scheduled_at'):
            tiktok['cancelled_scheduled_at'] = tiktok.pop('scheduled_at')
        tiktok.pop('buffer_post_id', None)
        tiktok.pop('buffer_due_at', None)
        tiktok['updated_at'] = datetime.now().isoformat(timespec='seconds')
        entry['tiktok'] = tiktok
        self.save_history()
        print(f"[YouTube] TikTok: agendamento {post_id} cancelado ('{stem}' → prepared)")
        return True

    def buffer_scheduled_posts(self) -> List[Dict]:
        """Posts com status 'scheduled' no canal TikTok do Buffer."""
        try:
            import requests
        except ImportError:
            raise Exception("requests não instalado (pip install requests)")
        buf = self._load_credential('buffer.json')
        headers = {'Content-Type': 'application/json',
                   'Authorization': f"Bearer {buf['token']}"}
        query = '''
        { posts(input:{organizationId: "%s"}) {
            edges { node { id status dueAt channelId text assets { mimeType type source thumbnail } } } } }''' % buf['organization_id']
        response = requests.post('https://api.buffer.com', headers=headers,
                                 json={'query': query}, timeout=60)
        data = response.json()
        if data.get('errors'):
            raise Exception(f"Buffer API: {data['errors'][0].get('message')}")
        nodes = [e['node'] for e in data['data']['posts']['edges']]
        return [n for n in nodes
                if n.get('channelId') == buf['tiktok_channel_id']
                and n.get('status') == 'scheduled']

    def tiktok_buffer_fill(self, limit: Optional[int] = None,
                           hour: int = 19) -> Dict:
        """
        Reabastece a fila do TikTok até o limite de posts agendados do plano.

        Regra de elegibilidade: publicado OU programado no YouTube + .mp4/.txt
        locais + sem agendamento/publicação TikTok ativo. Ordem: publicados
        primeiro (uploaded_at), depois os programados (scheduled_at do YouTube).
        Slots diários às `hour` (BRT), depois do último post já agendado.
        """
        from zoneinfo import ZoneInfo
        local_tz = ZoneInfo('America/Sao_Paulo')
        now = datetime.now(local_tz)

        published, programmed = [], []
        for stem, entry in self.history.items():
            if not isinstance(entry, dict) or entry.get('status') not in ('published', 'scheduled'):
                continue
            video = VIDEO_MAKER_DIR / f"{stem}.mp4"
            meta = VIDEO_MAKER_DIR / f"{stem}.txt"
            if not video.exists() or not meta.exists():
                continue
            tiktok = entry.get('tiktok') if isinstance(entry.get('tiktok'), dict) else {}
            if tiktok.get('status') in ('scheduled', 'published'):
                continue
            if entry.get('status') == 'published':
                published.append((entry.get('uploaded_at') or '9999', stem))
            else:
                programmed.append((entry.get('scheduled_at') or '9999', stem))
        eligible = [stem for _, stem in sorted(published)]
        eligible += [stem for _, stem in sorted(programmed)]

        scheduled = sorted(self.buffer_scheduled_posts(),
                           key=lambda n: n.get('dueAt') or '')
        buf_cfg = self._load_credential('buffer.json')
        cap = int(buf_cfg.get('scheduled_cap', 10))
        free = cap - len(scheduled)
        if limit is not None:
            free = min(free, limit)

        print(f"[YouTube] Fila TikTok: {len(scheduled)}/{cap} agendados | "
              f"{len(eligible)} elegíveis ({len(published)} publicados + "
              f"{len(programmed)} programados no YouTube) | {max(0, free)} vaga(s)")

        if free <= 0:
            print("  Nada a fazer — rode de novo quando posts forem publicados")
            return {'scheduled': 0, 'eligible': len(eligible), 'queue': len(scheduled)}

        # primeiro slot: hoje às `hour` se ainda futuro, senão amanhã;
        # se já existe fila, continua depois do último agendamento
        if scheduled:
            last = datetime.fromisoformat(
                scheduled[-1]['dueAt'].replace('Z', '+00:00')).astimezone(local_tz)
            first = last.replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            first = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if first <= now:
                first += timedelta(days=1)

        done, failed = [], []
        for index, stem in enumerate(eligible[:free]):
            when = first + timedelta(days=index)
            print(f"\n=== {stem} → {when.strftime('%d/%m %H:%M')} ===", flush=True)
            try:
                self.tiktok_buffer(VIDEO_MAKER_DIR / f"{stem}.mp4",
                                   VIDEO_MAKER_DIR / f"{stem}.txt", when)
                done.append(stem)
            except Exception as e:
                print(f"  ERRO: {e}", flush=True)
                failed.append((stem, str(e)[:200]))

        print(f"\n[YouTube] Fill: {len(done)} agendado(s) | {len(failed)} falha(s)")
        for stem, error in failed:
            print(f"  [ERRO] {stem} — {error}")
        return {'scheduled': len(done), 'failed': failed,
                'eligible': len(eligible), 'queue': len(scheduled) + len(done)}

def natural_language_to_datetime(text: str) -> Optional[datetime]:
    """
    Convert natural language time expressions to datetime objects
    
    Supported formats:
    - "terça às 6AM" -> next Tuesday at 6:00 AM
    - "amanhã às 19h" -> tomorrow at 7:00 PM
    - "daqui a 2 semanas" -> in 2 weeks
    - "daqui a 15 dias" -> in 15 days
    - "segunda-feira" -> next Monday
    - "dia 15 às 08:00" -> 15th of current month at 08:00
    - "2 de outubro às 07:30" -> October 2nd at 07:30
    """
    # This is a simplified implementation - in a real scenario, you'd want
    # to use a more sophisticated date parser like dateutil
    text = text.lower().strip()
    now = datetime.now()
    
    # Handle "daqui a X semanas/dias"
    if text.startswith("daqui a "):
        try:
            parts = text[8:].split()
            if len(parts) >= 2:
                amount = int(parts[0])
                unit = parts[1]
                
                if unit.startswith("semana") or unit.startswith("semanas"):
                    return now + timedelta(weeks=amount)
                elif unit.startswith("dia") or unit.startswith("dias"):
                    return now + timedelta(days=amount)
        except (ValueError, IndexError):
            pass
    
    # Handle "amanhã"
    if text.startswith("amanhã"):
        base_date = now + timedelta(days=1)
        time_part = text[7:].strip()  # Fixed: was [8:], should be [7:] to skip "amanhã" + space
        if time_part.startswith("às ") or time_part.startswith("as "):
            time_str = time_part[3:].strip()
            return _parse_time_string(base_date, time_str)
        return base_date.replace(hour=9, minute=0, second=0, microsecond=0)  # Default 9 AM
    
    # Handle day names
    weekdays = {
        'segunda': 0, 'terça': 1, 'quarta': 2, 'quinta': 3,
        'sexta': 4, 'sábado': 5, 'domingo': 6
    }
    
    for day_name, day_num in weekdays.items():
        if text.startswith(day_name):
            days_ahead = day_num - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            base_date = now + timedelta(days=days_ahead)
            time_part = text[len(day_name)+1:].strip()  # Fixed: was [len(day_name):], need to skip the space too
            
            if time_part.startswith("às ") or time_part.startswith("as "):
                time_str = time_part[3:].strip()
                return _parse_time_string(base_date, time_str)
            
            return base_date.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Handle "dia X às HH:MM" format
    dia_match = re.search(r'dia\s+(\d+)\s+às\s+(.+)', text)
    if dia_match:
        try:
            day = int(dia_match.group(1))
            time_str = dia_match.group(2).strip()
            
            # Get current month/year
            base_date = now.replace(day=day, hour=0, minute=0, second=0, microsecond=0)
            
            # If the day has already passed this month, go to next month
            if base_date < now.replace(hour=0, minute=0, second=0, microsecond=0):
                if base_date.month == 12:
                    base_date = base_date.replace(year=now.year + 1, month=1)
                else:
                    base_date = base_date.replace(month=base_date.month + 1)
            
            return _parse_time_string(base_date, time_str)
        except (ValueError, IndexError):
            pass
    
    # Handle "X de mês às HH:MM" format
    month_match = re.search(r'(\d+)\s+de\s+(\w+)\s+às\s+(.+)', text)
    if month_match:
        try:
            day = int(month_match.group(1))
            month_name = month_match.group(2)
            time_str = month_match.group(3).strip()
            
            # Map month names to numbers
            months = {
                'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
            }
            
            if month_name in months:
                month = months[month_name]
                year = now.year
                
                # If the month has already passed this year, go to next year
                if month < now.month or (month == now.month and day < now.day):
                    year += 1
                
                base_date = now.replace(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
                return _parse_time_string(base_date, time_str)
        except (ValueError, IndexError, KeyError):
            pass
    
    # If we get here, we couldn't parse it
    return None

def _parse_time_string(base_date: datetime, time_str: str) -> datetime:
    """Parse time string and apply to base_date"""
    try:
        # Handle formats like "6AM", "19h", "08:00", "07:30"
        # Clean up the string
        time_str = time_str.strip().lower()
        
        # Handle AM/PM notation
        if 'am' in time_str or 'pm' in time_str:
            # Extract the number and AM/PN
            match = re.search(r'(\d+)\s*(am|pm)', time_str)
            if match:
                hour = int(match.group(1))
                am_pm = match.group(2)
                
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
                
                return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Handle "HHh" format
        if time_str.endswith('h'):
            hour = int(time_str[:-1])
            return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Handle "HH:MM" format
        if ':' in time_str:
            parts = time_str.split(':')
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Handle just "HH" format
        hour = int(time_str)
        return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    except (ValueError, IndexError):
        # Return default time if parsing fails
        return base_date.replace(hour=9, minute=0, second=0, microsecond=0)

def main():
    parser = argparse.ArgumentParser(description='YouTube Growth Manager for OpenCode')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload a video to YouTube')
    upload_parser.add_argument('video_name', nargs='?', help='Name of video file (without extension)')
    upload_parser.add_argument('--file', '-f', help='Path to video file')
    upload_parser.add_argument('--force', action='store_true',
                               help=f'Publica mesmo com duração > {MAX_SHORT_DURATION_S:.0f}s '
                                    f'(exceção documentada ao duration gate)')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Schedule a video for future publication')
    schedule_parser.add_argument('video_name', nargs='?', help='Name of video file (without extension)')
    schedule_parser.add_argument('--file', '-f', help='Path to video file')
    schedule_parser.add_argument('--when', '-w', required=True, help='When to publish (natural language)')
    schedule_parser.add_argument('--force', action='store_true',
                                 help=f'Agenda mesmo com duração > {MAX_SHORT_DURATION_S:.0f}s '
                                      f'(exceção documentada ao duration gate)')
    
    # List schedule command
    subparsers.add_parser('schedule-list', help='List scheduled videos')
    
    # Cancel schedule command
    cancel_parser = subparsers.add_parser('schedule-cancel', help='Cancel a scheduled video')
    cancel_parser.add_argument('video_id', help='YouTube video ID to cancel')
    
    # Publish now command
    publish_parser = subparsers.add_parser('publish-now', help='Publish a scheduled video immediately')
    publish_parser.add_argument('video_id', help='YouTube video ID to publish')

    # Schedule existing command
    schedule_existing_parser = subparsers.add_parser(
        'schedule-existing',
        help='Schedule an already-uploaded private video for future publication'
    )
    schedule_existing_parser.add_argument('video_id', help='YouTube video ID to schedule')
    schedule_existing_parser.add_argument('--when', '-w', required=True,
                                          help='When to publish (natural language), e.g. "terça às 6AM"')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show channel analytics')
    analytics_parser.add_argument('--days', '-d', type=int, default=30, help='Number of days to analyze')

    # Comentário com CTA + link rastreável (WRITE público — exige --yes)
    comment_parser = subparsers.add_parser(
        'comment',
        help='Add the CTA comment (with tracked link) to a published video'
    )
    comment_parser.add_argument('target', help='Video name, .txt path or video_id')

    # SEO audit command (read-only)
    seo_parser = subparsers.add_parser(
        'seo-audit',
        help='Validate title/description against the inviolable SEO rules (read-only)'
    )
    seo_parser.add_argument('target', nargs='?',
                            help='metadata .txt path, video name or video_id')
    seo_parser.add_argument('--title', help='Title to validate directly')
    seo_parser.add_argument('--description', default='', help='Description to validate directly')
    seo_parser.add_argument('--history', action='store_true',
                            help='Audit every video recorded in the local history')

    # TikTok (pacote semi-manual — publicação feita por você no app/site)
    tiktok_pkg_parser = subparsers.add_parser(
        'tiktok-package',
        help='Generate a ready-to-paste TikTok caption package (SEO-gated, local only)'
    )
    tiktok_pkg_parser.add_argument('video_name', nargs='?',
                                   help='Name of video file (without extension)')
    tiktok_pkg_parser.add_argument('--file', '-f', help='Path to video file')

    subparsers.add_parser('tiktok-list', help='List TikTok packages and their status')

    tiktok_pub_parser = subparsers.add_parser(
        'tiktok-published',
        help='Mark a TikTok package as manually published'
    )
    tiktok_pub_parser.add_argument('target', help='Video name, .txt path or video_id')

    tiktok_buf_parser = subparsers.add_parser(
        'tiktok-buffer',
        help='Schedule automatic TikTok publishing via Buffer (SEO-gated, PUBLISH)'
    )
    tiktok_buf_parser.add_argument('video_name', nargs='?',
                                   help='Name of video file (without extension)')
    tiktok_buf_parser.add_argument('--file', '-f', help='Path to video file')
    tiktok_buf_parser.add_argument('--when', '-w', required=True,
                                   help='When to publish (natural language)')
    tiktok_buf_parser.add_argument('--force', action='store_true',
                                   help='Reagenda mesmo já existindo agendamento ativo')

    tiktok_buf_cancel = subparsers.add_parser(
        'tiktok-buffer-cancel',
        help='Cancel a scheduled TikTok post in Buffer'
    )
    tiktok_buf_cancel.add_argument('target', help='Video name or video_id')

    tiktok_fill_parser = subparsers.add_parser(
        'tiktok-buffer-fill',
        help='Top up the TikTok queue in Buffer with eligible videos (PUBLISH)'
    )
    tiktok_fill_parser.add_argument('--limit', '-l', type=int,
                                    help='Max videos to schedule in this run')
    tiktok_fill_parser.add_argument('--hour', type=int, default=19,
                                    help='Publishing hour in America/Sao_Paulo (default 19)')

    subparsers.add_parser(
        'tiktok-caption-sync',
        help='Re-saves the caption of posts already scheduled in Buffer '
             'from history.json (READ by default, WRITE with --yes)'
    )
    
    # Args for all commands
    parser.add_argument('--yes', '-y', action='store_true', help='Assume yes to prompts')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = YouTubeGrowthManager()
    
    if args.command == 'upload':
        # Find video files
        if args.video_name:
            pairs = manager.find_video_files(args.video_name)
        elif args.file:
            video_path = Path(args.file)
            metadata_path = video_path.with_suffix('.txt')
            if video_path.exists() and metadata_path.exists():
                pairs = [(video_path, metadata_path)]
            else:
                print(f"[YouTube] Error: Video or metadata file not found")
                print(f"  Video: {video_path}")
                print(f"  Metadata: {metadata_path}")
                return 1
        else:
            pairs = manager.find_video_files()
        
        if not pairs:
            print("[YouTube] No video files found to upload")
            return 1
        
        if len(pairs) > 1 and not args.video_name and not args.file:
            print("[YouTube] Multiple video files found:")
            for i, (video_path, metadata_path) in enumerate(pairs):
                print(f"  {i+1}. {video_path.name}")
            print("Please specify which video to upload using --video-name or --file")
            return 1
        
        video_path, metadata_path = pairs[0]
        
        # Confirm upload
        if not args.yes:
            metadata = manager.parse_metadata_file(metadata_path)
            print(f"[YouTube] About to upload:")
            print(f"  Title: {metadata['title']}")
            print(f"  Description: {metadata['description'][:100]}..." if len(metadata['description']) > 100 else f"  Description: {metadata['description']}")
            print(f"  Hashtags: {metadata['hashtags']}")
            
            response = input("\nProceed with upload? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Upload cancelled")
                return 0
        
        try:
            result = manager.upload_video(video_path, metadata_path,
                                          force_duration=getattr(args, 'force', False))
            print(f"\n[YouTube] Upload successful!")
            print(f"  Video ID: {result['video_id']}")
            print(f"  URL: {result['youtube_url']}")
            return 0
        except Exception as e:
            print(f"[YouTube] Upload failed: {e}")
            return 1
    
    elif args.command == 'schedule':
        # Find video files
        if args.video_name:
            pairs = manager.find_video_files(args.video_name)
        elif args.file:
            video_path = Path(args.file)
            metadata_path = video_path.with_suffix('.txt')
            if video_path.exists() and metadata_path.exists():
                pairs = [(video_path, metadata_path)]
            else:
                print(f"[YouTube] Error: Video or metadata file not found")
                print(f"  Video: {video_path}")
                print(f"  Metadata: {metadata_path}")
                return 1
        else:
            pairs = manager.find_video_files()
        
        if not pairs:
            print("[YouTube] No video files found to schedule")
            return 1
        
        if len(pairs) > 1 and not args.video_name and not args.file:
            print("[YouTube] Multiple video files found:")
            for i, (video_path, metadata_path) in enumerate(pairs):
                print(f"  {i+1}. {video_path.name}")
            print("Please specify which video to schedule using --video-name or --file")
            return 1
        
        video_path, metadata_path = pairs[0]
        
        # Parse natural language time
        scheduled_time = natural_language_to_datetime(args.when)
        if not scheduled_time:
            print(f"[YouTube] Could not parse time expression: '{args.when}'")
            print("Please use formats like:")
            print("  'terça às 6AM'")
            print("  'amanhã às 19h'")
            print("  'daqui a 2 semanas'")
            print("  'segunda-feira'")
            print("  'dia 15 às 08:00'")
            print("  '2 de outubro às 07:30'")
            return 1
        
        # Check if time is in the past
        if scheduled_time < datetime.now():
            print(f"[YouTube] Scheduled time is in the past: {scheduled_time}")
            return 1
        
        # Confirm scheduling
        if not args.yes:
            metadata = manager.parse_metadata_file(metadata_path)
            print(f"[YouTube] About to schedule:")
            print(f"  Title: {metadata['title']}")
            print(f"  Scheduled for: {scheduled_time.strftime('%A, %d/%m/%Y %H:%M')}")
            print(f"  Timezone: America/Sao_Paulo")
            
            response = input("\nProceed with scheduling? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Scheduling cancelled")
                return 0
        
        try:
            result = manager.upload_video(video_path, metadata_path, scheduled_time,
                                          force_duration=getattr(args, 'force', False))
            print(f"\n[YouTube] Scheduling successful!")
            print(f"  Video ID: {result['video_id']}")
            print(f"  URL: {result['youtube_url']}")
            print(f"  Scheduled for: {scheduled_time.strftime('%A, %d/%m/%Y %H:%M %Z')}")
            return 0
        except Exception as e:
            print(f"[YouTube] Scheduling failed: {e}")
            return 1
    
    elif args.command == 'schedule-list':
        scheduled = manager.list_scheduled_videos()
        if not scheduled:
            print("[YouTube] No scheduled videos found")
            return 0
        
        print("[YouTube] Scheduled Videos:")
        print("-" * 80)
        for entry in scheduled:
            scheduled_time = datetime.fromisoformat(entry['scheduled_at']) if entry.get('scheduled_at') else None
            time_str = scheduled_time.strftime('%A, %d/%m/%Y %H:%M') if scheduled_time else 'Unknown'
            print(f"Title: {entry['title']}")
            print(f"Video ID: {entry['video_id']}")
            print(f"Scheduled for: {time_str}")
            video_url = entry.get('youtube_url') or 'https://www.youtube.com/watch?v=' + str(entry.get('video_id', ''))
            print(f"URL: {video_url}")
            print("-" * 80)
        return 0
    
    elif args.command == 'schedule-cancel':
        if not args.yes:
            response = input(f"Are you sure you want to cancel scheduled publication for video {args.video_id}? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Cancel operation cancelled")
                return 0
        
        success = manager.cancel_scheduled_video(args.video_id)
        if success:
            print(f"[YouTube] Successfully cancelled scheduled publication for {args.video_id}")
            return 0
        else:
            print(f"[YouTube] Failed to cancel scheduled publication for {args.video_id}")
            return 1
    
    elif args.command == 'publish-now':
        if not args.yes:
            response = input(f"Are you sure you want to publish video {args.video_id} immediately? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Publish now operation cancelled")
                return 0
        
        success = manager.publish_now(args.video_id)
        if success:
            print(f"[YouTube] Successfully published video {args.video_id} immediately")
            return 0
        else:
            print(f"[YouTube] Failed to publish video {args.video_id} immediately")
            return 1

    elif args.command == 'comment':
        # WRITE público: comentário visível no vídeo
        if not args.yes:
            response = input(
                f"Adicionar comentário com link em '{args.target}'? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Comentário cancelado")
                return 0
        comment_id = manager.comment_video(args.target)
        if comment_id:
            print(f"[YouTube] Comentário criado: {comment_id}")
            return 0
        return 1

    elif args.command == 'schedule-existing':
        scheduled_time = natural_language_to_datetime(args.when)
        if not scheduled_time:
            print(f"[YouTube] Could not parse time expression: '{args.when}'")
            print("Please use formats like:")
            print("  'terça às 6AM'")
            print("  'amanhã às 19h'")
            print("  'segunda-feira'")
            return 1

        if not args.yes:
            response = input(
                f"Schedule video {args.video_id} for {scheduled_time.strftime('%A, %d/%m/%Y %H:%M')}? (y/N): "
            )
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Schedule operation cancelled")
                return 0

        success = manager.schedule_existing_publish(args.video_id, scheduled_time)
        if success:
            print(f"[YouTube] Successfully scheduled video {args.video_id}")
            return 0
        else:
            print(f"[YouTube] Failed to schedule video {args.video_id}")
            return 1

    elif args.command == 'analytics':
        # Placeholder for analytics implementation
        print("[YouTube] Analytics feature coming soon...")
        print("This will show:")
        print(f"  - Views, likes, comments over last {args.days} days")
        print("  - Top performing videos")
        print("  - Audience demographics")
        print("  - Traffic sources")
        return 0
    
    elif args.command == 'seo-audit':
        # READ/ANALYZE: nunca modifica metadados
        if args.history:
            failures = 0
            deleted = 0
            live = {k: v for k, v in manager.history.items()
                    if isinstance(v, dict) and v.get('status') != 'deleted'}
            deleted = len(manager.history) - len(live)
            print(f"[YouTube] SEO audit — local history ({len(live)} vídeos ativos"
                  f"{f', {deleted} deletados ignorados' if deleted else ''})")
            for stem, entry in live.items():
                errors = manager.seo_audit(entry.get('title', ''), entry.get('description', ''))
                if errors:
                    failures += 1
                print(f"  [{'FAIL' if errors else 'PASS'}] {stem} — {entry.get('title', '')}")
                for error in errors:
                    print(f"           - {error}")
            print(f"[YouTube] {failures}/{len(live)} vídeo(s) fora do padrão")
            return 1 if failures else 0

        if args.title is not None:
            errors = manager.seo_audit(args.title, args.description)
        elif args.target:
            path = Path(args.target).expanduser()
            entry = None
            metadata = None

            if path.suffix == '.txt' and path.exists():
                metadata = manager.parse_metadata_file(path)
            elif args.target in manager.history:
                entry = manager.history[args.target]
            else:
                for value in manager.history.values():
                    if value.get('video_id') == args.target:
                        entry = value
                        break
                if entry is None:
                    pairs = manager.find_video_files(args.target)
                    if pairs:
                        metadata = manager.parse_metadata_file(pairs[0][1])

            if metadata:
                errors = manager.seo_audit(metadata['title'], metadata['description'])
            elif entry:
                errors = manager.seo_audit(entry.get('title', ''), entry.get('description', ''))
            else:
                print(f"[YouTube] Target not found: {args.target}")
                print("  Use um caminho .txt, um nome de vídeo, um video_id ou --history")
                return 1
        else:
            print("[YouTube] seo-audit: informe --title/--description, um arquivo .txt, "
                  "um nome de vídeo, um video_id ou --history")
            return 1

        if errors:
            print("[YouTube] SEO audit FAIL (regra inviolável):")
            for error in errors:
                print(f"  - {error}")
            return 1

        print("[YouTube] SEO audit PASS — keyword no início, sem abreviações")
        return 0

    elif args.command == 'tiktok-package':
        if args.video_name:
            pairs = manager.find_video_files(args.video_name)
        elif args.file:
            video_path = Path(args.file)
            metadata_path = video_path.with_suffix('.txt')
            if video_path.exists() and metadata_path.exists():
                pairs = [(video_path, metadata_path)]
            else:
                print("[YouTube] Error: Video or metadata file not found")
                print(f"  Video: {video_path}")
                print(f"  Metadata: {metadata_path}")
                return 1
        else:
            pairs = manager.find_video_files()

        if not pairs:
            print("[YouTube] No video files found")
            return 1

        if len(pairs) > 1 and not args.video_name and not args.file:
            print("[YouTube] Multiple video files found:")
            for i, (video_path, metadata_path) in enumerate(pairs):
                print(f"  {i+1}. {video_path.name}")
            print("Specify which video using the name or --file")
            return 1

        video_path, metadata_path = pairs[0]
        try:
            manager.tiktok_package(video_path, metadata_path)
            return 0
        except Exception as e:
            print(f"[YouTube] TikTok package failed: {e}")
            return 1

    elif args.command == 'tiktok-list':
        items = manager.tiktok_list()
        if not items:
            print("[YouTube] Nenhum pacote TikTok registrado")
            return 0
        print("[YouTube] Pacotes TikTok:")
        print("-" * 80)
        for item in items:
            print(f"Título: {item['title']}")
            print(f"Status: {item['status']}")
            if item['caption_file']:
                print(f"Legenda: {item['caption_file']}")
            if item['buffer_post_id']:
                print(f"Post Buffer: {item['buffer_post_id']}")
            if item['scheduled_at']:
                print(f"Agendado: {item['scheduled_at']}")
            if item['prepared_at']:
                print(f"Preparado: {item['prepared_at']}")
            if item['published_at']:
                print(f"Publicado: {item['published_at']}")
            print("-" * 80)
        prepared = sum(1 for i in items if i['status'] == 'prepared')
        scheduled = sum(1 for i in items if i['status'] == 'scheduled')
        published = sum(1 for i in items if i['status'] == 'published')
        print(f"[YouTube] {prepared} pendentes | {scheduled} agendados | "
              f"{published} publicados")
        return 0

    elif args.command == 'tiktok-published':
        if manager.tiktok_mark_published(args.target):
            return 0
        return 1

    elif args.command == 'tiktok-buffer':
        if args.video_name:
            pairs = manager.find_video_files(args.video_name)
        elif args.file:
            video_path = Path(args.file)
            metadata_path = video_path.with_suffix('.txt')
            if video_path.exists() and metadata_path.exists():
                pairs = [(video_path, metadata_path)]
            else:
                print("[YouTube] Error: Video or metadata file not found")
                return 1
        else:
            pairs = manager.find_video_files()

        if not pairs:
            print("[YouTube] No video files found")
            return 1
        if len(pairs) > 1 and not args.video_name and not args.file:
            print("[YouTube] Multiple video files found:")
            for i, (video_path, metadata_path) in enumerate(pairs):
                print(f"  {i+1}. {video_path.name}")
            print("Specify which video using the name or --file")
            return 1

        video_path, metadata_path = pairs[0]
        scheduled_time = natural_language_to_datetime(args.when)
        if not scheduled_time:
            print(f"[YouTube] Could not parse time expression: '{args.when}'")
            print("Exemplos: 'amanhã às 19h' | 'sexta às 18:30' | 'dia 5 às 12:00'")
            return 1

        if not args.yes:
            metadata = manager.parse_metadata_file(metadata_path)
            print("[YouTube] About to schedule on TikTok via Buffer:")
            print(f"  Title: {metadata['title']}")
            print(f"  Video: {video_path.name}")
            print(f"  When: {scheduled_time.strftime('%A, %d/%m/%Y %H:%M')} "
                  f"America/Sao_Paulo")
            print("  Mode: automatic (publicação automática)")
            response = input("\nProceed with scheduling? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Scheduling cancelled")
                return 0

        try:
            result = manager.tiktok_buffer(video_path, metadata_path, scheduled_time,
                                           force=args.force)
            print(f"\n[YouTube] TikTok scheduling done!")
            print(f"  Buffer post: {result['post_id']}")
            print(f"  Scheduled: {result['scheduled_at']}")
            return 0
        except Exception as e:
            print(f"[YouTube] TikTok scheduling failed: {e}")
            return 1

    elif args.command == 'tiktok-buffer-cancel':
        if not args.yes:
            response = input(f"Cancel Buffer scheduling for '{args.target}'? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Cancel operation cancelled")
                return 0
        try:
            if manager.tiktok_buffer_cancel(args.target):
                return 0
            return 1
        except Exception as e:
            print(f"[YouTube] Cancel failed: {e}")
            return 1

    elif args.command == 'tiktok-buffer-fill':
        if not args.yes:
            response = input("Top up the TikTok queue in Buffer? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Fill cancelled")
                return 0
        try:
            manager.tiktok_buffer_fill(limit=args.limit, hour=args.hour)
            return 0
        except Exception as e:
            print(f"[YouTube] Fill failed: {e}")
            return 1

    elif args.command == 'tiktok-caption-sync':
        execute = bool(args.yes)
        if execute:
            response = input(
                "Atualizar a legenda dos posts já agendados no Buffer? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[YouTube] Sync cancelado")
                return 0
        try:
            res = manager.tiktok_caption_sync(execute=execute)
        except Exception as e:
            print(f"[YouTube] tiktok-caption-sync falhou: {e}")
            return 1

        mode = 'APLICADO' if execute else 'DRY-RUN (sem --yes, nada foi alterado)'
        print(f"\n[YouTube] Legenda Buffer sync — {mode}")
        print(f"  iguais (não precisa mudar): {len(res['same'])}")
        label = 'atualizados' if execute else 'a atualizar'
        print(f"  {label}: {len(res['updated'])}")
        for stem, post_id in res['updated']:
            print(f"    - {stem}  ({post_id})")
        if res['skipped']:
            print(f"  ignorados: {len(res['skipped'])}")
            for stem, why in res['skipped']:
                print(f"    - {stem}: {why}")
        if res['missing']:
            print(f"  fora da fila do Buffer (já publicou ou cancelou): "
                  f"{len(res['missing'])}")
            for stem, post_id in res['missing']:
                print(f"    - {stem}  ({post_id})")
        return 0

    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())