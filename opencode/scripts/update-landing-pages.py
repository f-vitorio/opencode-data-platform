#!/usr/bin/env python3
"""
Script para atualizar landing pages de nicho com CTA WhatsApp e depoimentos
"""

import os
import re
from pathlib import Path

# Configuração das landing pages
LANDING_PAGES = {
    "landing-page-para-advogados.astro": {
        "niche": "advocacia",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para meu escritório de advocacia.",
        "testimonial": {
            "name": "Dr. Ricardo Santos",
            "role": "Escritório Santos & Associados",
            "text": "Triplicamos os contatos qualificados em 2 meses. O investimento se pagou em 15 dias."
        },
        "color": "amber"
    },
    "landing-page-para-clinicas.astro": {
        "niche": "clínicas",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para minha clínica.",
        "testimonial": {
            "name": "Dra. Ana Costa",
            "role": "Clínica Costa Médica",
            "text": "A agenda lotou em 30 dias. Recebemos 47 agendamentos qualificados no primeiro mês."
        },
        "color": "emerald"
    },
    "landing-page-para-contadores.astro": {
        "niche": "contabilidade",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para meu escritório de contabilidade.",
        "testimonial": {
            "name": "Carlos Oliveira",
            "role": "Contabilidade Oliveira",
            "text": "Em 45 dias, captamos 23 empresas novas. O ROI foi de 8x o investimento em ads."
        },
        "color": "blue"
    },
    "landing-page-para-imobiliaria.astro": {
        "niche": "imobiliária",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para minha imobiliária.",
        "testimonial": {
            "name": "Marcos Silva",
            "role": "Imobiliária Silva",
            "text": "Recebemos 89 leads qualificados em 2 meses. Fechamos 12 vendas a partir dos anúncios."
        },
        "color": "purple"
    },
    "landing-page-para-esteticistas.astro": {
        "niche": "estética",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para minha clínica de estética.",
        "testimonial": {
            "name": "Dra. Mariana Costa",
            "role": "Clínica Costa Estética",
            "text": "A agenda de procedimentos estéticos lotou em 25 dias. Faturamento cresceu 180%."
        },
        "color": "pink"
    },
    "landing-page-para-fisioterapeutas.astro": {
        "niche": "fisioterapia",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para meu consultório de fisioterapia.",
        "testimonial": {
            "name": "Ricardo Mendes",
            "role": "Fisio Clinic",
            "text": "Em 30 dias, triplicamos os agendamentos. O custo por paciente caiu 60%."
        },
        "color": "teal"
    },
    "landing-page-para-psicologos.astro": {
        "niche": "psicologia",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para meu consultório de psicologia.",
        "testimonial": {
            "name": "Dra.fernanda Lima",
            "role": "Psiclinic",
            "text": "Recebemos 52 agendamentos no primeiro mês. A agenda de atendimentos está lotada."
        },
        "color": "indigo"
    },
    "landing-page-para-arquitetos.astro": {
        "niche": "arquitetura",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para meu escritório de arquitetura.",
        "testimonial": {
            "name": "João Pereira",
            "role": "Arquitetos Associados",
            "text": "Em 2 meses, fechamos 4 projetos de alto valor. O retorno foi 12x o investimento."
        },
        "color": "orange"
    },
    "landing-page-para-infoprodutor.astro": {
        "niche": "infoprodutos",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para meu infoproduto.",
        "testimonial": {
            "name": "Pedro Santos",
            "role": "Criador de Conteúdo",
            "text": "As vendas do meu curso online aumentaram 340% em 45 dias. Conversão absurda."
        },
        "color": "violet"
    },
    "landing-page-para-dentistas.astro": {
        "niche": "odontologia",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para minha clínica odontológica.",
        "testimonial": {
            "name": "Dr. Paulo Mendes",
            "role": "OdontoClínica",
            "text": "Em 30 dias, recebemos 67 agendamentos. A agenda de implantes está lotada."
        },
        "color": "cyan"
    },
    "landing-page-para-medicos.astro": {
        "niche": "medicina",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para meu consultório médico.",
        "testimonial": {
            "name": "Dr. André Costa",
            "role": "Costa Medicina",
            "text": "Triplicamos os agendamentos em 45 dias. O retorno sobre investimento foi excelente."
        },
        "color": "red"
    },
    "landing-page-para-escritorios-de-arquitetura.astro": {
        "niche": "arquitetura",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para meu escritório de arquitetura.",
        "testimonial": {
            "name": "Ana Paula Silva",
            "role": "Silva Arquitetura",
            "text": "Em 2 meses, fechamos 3 projetos de alto padrão. O investimento se pagou rapidamente."
        },
        "color": "orange"
    },
    "landing-page-para-imobiliarias.astro": {
        "niche": "imobiliária",
        "whatsapp_message": "Olá! Vim pelo site. Tenho interesse em Landing Page para minha imobiliária.",
        "testimonial": {
            "name": "Roberto Almeida",
            "role": "Almeida Imóveis",
            "text": "Recebemos 73 leads qualificados em 30 dias. Fechamos 8 vendas a partir dos anúncios."
        },
        "color": "purple"
    }
}

def update_landing_page(filename, config):
    """Atualiza uma landing page com CTA WhatsApp e depoimento."""
    filepath = Path(f"/home/fvitorio/Documents/Agencia_ebano/FVS7/fvs7/src/pages/{filename}")
    
    if not filepath.exists():
        print(f"❌ Arquivo não encontrado: {filename}")
        return False
    
    content = filepath.read_text(encoding='utf-8')
    
    # 1. Adicionar import do MessageCircle se não existir
    if "MessageCircle" not in content:
        # Encontrar a linha de import do lucide-react
        import_pattern = r'import \{[^}]+\} from "lucide-react";'
        match = re.search(import_pattern, content)
        if match:
            old_import = match.group(0)
            # Adicionar MessageCircle ao import
            new_import = old_import.replace('}', ', MessageCircle}')
            content = content.replace(old_import, new_import)
            print(f"  ✅ Import do MessageCircle adicionado")
    
    # 2. Encontrar e substituir o CTA do hero
    # Padrão para encontrar a seção do hero com o CTA
    hero_cta_pattern = r'<div class="flex flex-col sm:flex-row items-center justify-center gap-4">.*?</div>\s*</div>\s*</div>\s*</header>'
    hero_match = re.search(hero_cta_pattern, content, re.DOTALL)
    
    if hero_match:
        old_hero_cta = hero_match.group(0)
        
        # Criar novo CTA com WhatsApp
        new_hero_cta = f'''<div class="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href="https://wa.me/5511999999999?text={config['whatsapp_message'].replace(' ', '%20').replace('!', '%21').replace('á', '%C3%A1').replace('ã', '%C3%A3')}"
                target="_blank"
                rel="noopener noreferrer"
                class="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-green-500 hover:bg-green-600 rounded-lg transition-all duration-300 shadow-[0_0_20px_rgba(34,197,94,0.4)] hover:shadow-[0_0_30px_rgba(34,197,94,0.6)] transform hover:-translate-y-1 w-full sm:w-auto"
              >
                <span class="relative z-10 flex items-center gap-2">
                  <MessageCircle size={{20}} class="fill-current" />
                  Fale no WhatsApp
                </span>
              </a>
              <a
                href="/atendimento/"
                class="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-{config['color']}-600 hover:bg-{config['color']}-500 rounded-lg transition-all duration-300 shadow-[0_0_20px_rgba(var(--tw-color-{config['color']}-600),0.4)] hover:shadow-[0_0_30px_rgba(var(--tw-color-{config['color']}-600),0.6)] transform hover:-translate-y-1 w-full sm:w-auto"
              >
                <span class="relative z-10 flex items-center gap-2">
                  Solicitar Atendimento
                  <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </span>
              </a>
            </div>

            <div class="mt-8 p-4 bg-slate-800/50 rounded-xl border border-slate-700/50 max-w-md mx-auto">
              <div class="flex items-center justify-center gap-1 mb-2">
                {{Array.from({{ length: 5 }}).map(() => (
                  <svg class="w-4 h-4 text-yellow-400 fill-current" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}}
              </div>
              <p class="text-slate-300 text-sm italic mb-2">"{config['testimonial']['text']}"</p>
              <p class="text-slate-400 text-xs font-medium">— {config['testimonial']['name']}, {config['testimonial']['role']}</p>
            </div>
          </div>
        </div>
      </header>'''
        
        content = content.replace(old_hero_cta, new_hero_cta)
        print(f"  ✅ CTA WhatsApp e depoimento adicionados")
    
    # Salvar arquivo
    filepath.write_text(content, encoding='utf-8')
    print(f"  💾 Arquivo salvo: {filename}")
    return True

def main():
    """Função principal."""
    print("🚀 Atualizando landing pages de nicho com CTA WhatsApp...")
    print()
    
    success_count = 0
    error_count = 0
    
    for filename, config in LANDING_PAGES.items():
        print(f"📝 Processando: {filename}")
        try:
            if update_landing_page(filename, config):
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            error_count += 1
        print()
    
    print(f"📊 Resultado: {success_count} sucesso, {error_count} erros")

if __name__ == "__main__":
    main()
