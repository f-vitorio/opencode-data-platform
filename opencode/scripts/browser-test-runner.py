#!/usr/bin/env python3
"""
Browser Test Runner - CLI Wrapper para Playwright Automation

Uso:
    python browser-test-runner.py https://exemplo.com --mode CRO_VALIDATION
    python browser-test-runner.py https://exemplo.com --mode SMOKE --headed
    python browser-test-runner.py https://exemplo.com --mode FULL_E2E --slug meu-teste
"""

import sys
import os
import argparse
import json
from pathlib import Path

# Adicionar skills ao path
skills_path = Path(__file__).parent.parent / "skills" / "playwright-automation"
sys.path.insert(0, str(skills_path))

try:
    from playwright_automation.runner import BrowserTestRunner
except ImportError as e:
    print(f"Erro ao importar skill: {e}")
    print("Verifique se a skill playwright-automation está instalada corretamente.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Browser Test Runner - Testes E2E com Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modos disponíveis:
  SMOKE           - Validação rápida (30s): HTTP, title, H1, CTA, console errors
  FULL_E2E        - Fluxo completo (2-5min): navegação, CTA, formulário, thank you
  CRO_VALIDATION  - Foco conversão (2-3min): CTA, form, prova social, confiança, performance
  SEO_TECHNICAL   - SEO técnico (2-3min): meta, headings, schema, images, canonical
  MOBILE_FIRST    - Responsividade (1-2min): 5 viewports, touch targets, font sizes

Exemplos:
  %(prog)s https://meusite.com --mode CRO_VALIDATION
  %(prog)s http://localhost:4321 --mode SMOKE --headed
  %(prog)s https://cliente.com --mode FULL_E2E --slug auditoria-cliente
        """
    )
    
    parser.add_argument("url", help="URL para testar")
    parser.add_argument(
        "--mode", "-m",
        default="SMOKE",
        choices=["SMOKE", "FULL_E2E", "CRO_VALIDATION", "SEO_TECHNICAL", "MOBILE_FIRST"],
        help="Modo de teste (padrão: SMOKE)"
    )
    parser.add_argument(
        "--slug", "-s",
        help="Slug personalizado para diretório de relatório (padrão: derivado do domínio)"
    )
    parser.add_argument(
        "--headed", "-H",
        action="store_true",
        help="Executar com browser visível (headed mode)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Saída apenas JSON (para integração)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Diretório base para relatórios (padrão: ~/Documents/PROJETOS/audits)"
    )
    
    args = parser.parse_args()
    
    # Configurar diretório de saída customizado
    if args.output_dir:
        os.environ["AUDIT_BASE_DIR"] = args.output_dir
    
    print(f"\n{'='*60}")
    print(f"BROWSER TEST RUNNER")
    print(f"{'='*60}")
    print(f"URL: {args.url}")
    print(f"Mode: {args.mode}")
    print(f"Headed: {'Sim' if args.headed else 'Não (headless)'}")
    print(f"{'='*60}\n")
    
    try:
        runner = BrowserTestRunner(
            url=args.url,
            mode=args.mode,
            slug=args.slug,
            headed=args.headed
        )
        
        result = runner.run()
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"RESULTADO")
            print(f"{'='*60}")
            print(f"Status: {result['status']}")
            print(f"Score: {result['score']['overall']}/100")
            print(f"Duração: {result['duration_ms']/1000:.1f}s")
            print(f"Screenshots: {len(result['screenshots'])}")
            print(f"Console Errors: {len(result['console_errors'])}")
            print(f"Network Failures: {len(result['network_failures'])}")
            print(f"\nRelatório: {runner.audit_dir / f'{runner.slug}_report.md'}")
            print(f"JSON: {runner.audit_dir / f'{runner.slug}_report.json'}")
            print(f"{'='*60}\n")
            
            if result["critical_issues"]:
                print("PROBLEMAS CRÍTICOS (P0):")
                for issue in result["critical_issues"]:
                    print(f"  - {issue['message']}")
                print()
            
            if result["warnings"]:
                print("AVISOS (P1/P2):")
                for w in result["warnings"][:10]:  # Limitar a 10
                    print(f"  [{w.get('priority', 'P2')}] {w['message']}")
                if len(result["warnings"]) > 10:
                    print(f"  ... e mais {len(result['warnings']) - 10} avisos")
                print()
            
            print("PRÓXIMOS PASSOS:")
            for step in result["next_steps"][:5]:
                print(f"  {step}")
        
        # Exit code baseado no status
        if result["status"] == "FAIL":
            sys.exit(1)
        elif result["status"] == "WARN":
            sys.exit(2)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
        sys.exit(130)
    except Exception as e:
        print(f"\nErro durante execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()