#!/bin/bash
# Script para atualizar landing pages com CTA WhatsApp

PAGES_DIR="/home/fvitorio/Documents/Agencia_ebano/FVS7/fvs7/src/pages"

# Lista de landing pages e suas configurações
declare -A PAGES
PAGES["landing-page-para-advogados.astro"]="advogados|Olá! Vim pelo site. Tenho interesse em Landing Page para meu escritório de advocacia.|Dr. Ricardo Santos|Escritório Santos & Associados|Triplicamos os contatos qualificados em 2 meses. O investimento se pagou em 15 dias.|amber"
PAGES["landing-page-para-clinicas.astro"]="clínicas|Olá! Vim pelo site. Tenho interesse em Landing Page para minha clínica.|Dra. Ana Costa|Clínica Costa Médica|A agenda lotou em 30 dias. Recebemos 47 agendamentos qualificados no primeiro mês.|emerald"
PAGES["landing-page-para-contadores.astro"]="contabilidade|Olá! Vim pelo site. Tenho interesse em Landing Page para meu escritório de contabilidade.|Carlos Oliveira|Contabilidade Oliveira|Em 45 dias, captamos 23 empresas novas. O ROI foi de 8x o investimento em ads.|blue"
PAGES["landing-page-para-imobiliaria.astro"]="imobiliária|Olá! Vim pelo site. Tenho interesse em Landing Page para minha imobiliária.|Marcos Silva|Imobiliária Silva|Recebemos 89 leads qualificados em 2 meses. Fechamos 12 vendas a partir dos anúncios.|purple"
PAGES["landing-page-para-esteticistas.astro"]="estética|Olá! Vim pelo site. Tenho interesse em Landing Page para minha clínica de estética.|Dra. Mariana Costa|Clínica Costa Estética|A agenda de procedimentos estéticos lotou em 25 dias. Faturamento cresceu 180%.|pink"
PAGES["landing-page-para-fisioterapeutas.astro"]="fisioterapia|Olá! Vim pelo site. Tenho interesse em Landing Page para meu consultório de fisioterapia.|Ricardo Mendes|Fisio Clinic|Em 30 dias, triplicamos os agendamentos. O custo por paciente caiu 60%.|teal"
PAGES["landing-page-para-psicologos.astro"]="psicologia|Olá! Vim pelo site. Tenho interesse em Landing Page para meu consultório de psicologia.|Dra. Fernanda Lima|Psiclinic|Recebemos 52 agendamentos no primeiro mês. A agenda de atendimentos está lotada.|indigo"
PAGES["landing-page-para-arquitetos.astro"]="arquitetura|Olá! Vim pelo site. Tenho interesse em Landing Page para meu escritório de arquitetura.|João Pereira|Arquitetos Associados|Em 2 meses, fechamos 4 projetos de alto valor. O retorno foi 12x o investimento.|orange"
PAGES["landing-page-para-infoprodutor.astro"]="infoprodutos|Olá! Vim pelo site. Tenho interesse em Landing Page para meu infoproduto.|Pedro Santos|Criador de Conteúdo|As vendas do meu curso online aumentaram 340% em 45 dias. Conversão absurda.|violet"
PAGES["landing-page-para-dentistas.astro"]="odontologia|Olá! Vim pelo site. Tenho interesse em Landing Page para minha clínica odontológica.|Dr. Paulo Mendes|OdontoClínica|Em 30 dias, recebemos 67 agendamentos. A agenda de implantes está lotada.|cyan"
PAGES["landing-page-para-medicos.astro"]="medicina|Olá! Vim pelo site. Tenho interesse em Landing Page para meu consultório médico.|Dr. André Costa|Costa Medicina|Triplicamos os agendamentos em 45 dias. O retorno sobre investimento foi excelente.|red"
PAGES["landing-page-para-escritorios-de-arquitetura.astro"]="arquitetura|Olá! Vim pelo site. Tenho interesse em Landing Page para meu escritório de arquitetura.|Ana Paula Silva|Silva Arquitetura|Em 2 meses, fechamos 3 projetos de alto padrão. O investimento se pagou rapidamente.|orange"
PAGES["landing-page-para-imobiliarias.astro"]="imobiliária|Olá! Vim pelo site. Tenho interesse em Landing Page para minha imobiliária.|Roberto Almeida|Almeida Imóveis|Recebemos 73 leads qualificados em 30 dias. Fechamos 8 vendas a partir dos anúncios.|purple"

echo "🚀 Atualizando landing pages com CTA WhatsApp..."
echo

for page in "${!PAGES[@]}"; do
    IFS='|' read -r niche message name role testimonial color <<< "${PAGES[$page]}"
    
    echo "📝 Processando: $page"
    
    # Verificar se o arquivo existe
    if [ ! -f "$PAGES_DIR/$page" ]; then
        echo "  ❌ Arquivo não encontrado"
        continue
    fi
    
    # Verificar se já tem MessageCircle
    if ! grep -q "MessageCircle" "$PAGES_DIR/$page"; then
        # Adicionar MessageCircle ao import
        sed -i 's/import { \(.*\) } from "lucide-react";/import { \1, MessageCircle } from "lucide-react";/' "$PAGES_DIR/$page"
        echo "  ✅ Import do MessageCircle adicionado"
    fi
    
    # Criar arquivo temporário com as alterações
    TEMP_FILE=$(mktemp)
    
    # Usar awk para fazer as alterações
    awk -v niche="$niche" -v message="$message" -v name="$name" -v role="$role" -v testimonial="$testimonial" -v color="$color" '
    /<div class="flex flex-col sm:flex-row items-center justify-center gap-4">/ {
        print "            <div class=\"flex flex-col sm:flex-row items-center justify-center gap-4\">"
        print "              <a"
        print "                href=\"https://wa.me/5511999999999?text=" message "\""
        print "                target=\"_blank\""
        print "                rel=\"noopener noreferrer\""
        print "                class=\"group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-green-500 hover:bg-green-600 rounded-lg transition-all duration-300 shadow-[0_0_20px_rgba(34,197,94,0.4)] hover:shadow-[0_0_30px_rgba(34,197,94,0.6)] transform hover:-translate-y-1 w-full sm:w-auto\""
        print "              >"
        print "                <span class=\"relative z-10 flex items-center gap-2\">"
        print "                  <MessageCircle size={20} class=\"fill-current\" />"
        print "                  Fale no WhatsApp"
        print "                </span>"
        print "              </a>"
        print "              <a"
        print "                href=\"/atendimento/\""
        print "                class=\"group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white bg-" color "-600 hover:bg-" color "-500 rounded-lg transition-all duration-300 shadow-[0_0_20px_rgba(var(--tw-color-" color "-600),0.4)] hover:shadow-[0_0_30px_rgba(var(--tw-color-" color "-600),0.6)] transform hover:-translate-y-1 w-full sm:w-auto\""
        print "              >"
        print "                <span class=\"relative z-10 flex items-center gap-2\">"
        print "                  Solicitar Atendimento"
        print "                  <ArrowRight class=\"w-5 h-5 group-hover:translate-x-1 transition-transform\" />"
        print "                </span>"
        print "              </a>"
        print "            </div>"
        print ""
        print "            <div class=\"mt-8 p-4 bg-slate-800/50 rounded-xl border border-slate-700/50 max-w-md mx-auto\">"
        print "              <div class=\"flex items-center justify-center gap-1 mb-2\">"
        print "                {Array.from({ length: 5 }).map(() => ("
        print "                  <svg class=\"w-4 h-4 text-yellow-400 fill-current\" viewBox=\"0 0 20 20\">"
        print "                    <path d=\"M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z\" />"
        print "                  </svg>"
        print "                ))}"
        print "              </div>"
        print "              <p class=\"text-slate-300 text-sm italic mb-2\">\"" testimonial "\"</p>"
        print "              <p class=\"text-slate-400 text-xs font-medium\">— " name ", " role "</p>"
        print "            </div>"
        next
    }
    
    # Pular linhas antigas do CTA até encontrar o fechamento
    /SOLICITAR ATENDIMENTO ESTRATÉGICO/ || /SOLICITAR ANÁLISE GRATUITA/ || /SOLICITAR ORÇAMENTO/ {
        # Pular até encontrar o fechamento do header
        while (getline > 0) {
            if (/<\/header>/) {
                print
                break
            }
        }
        next
    }
    
    # Imprimir outras linhas normalmente
    { print }
    ' "$PAGES_DIR/$page" > "$TEMP_FILE"
    
    # Substituir o arquivo original
    mv "$TEMP_FILE" "$PAGES_DIR/$page"
    
    echo "  ✅ CTA WhatsApp e depoimento adicionados"
    echo "  💾 Arquivo salvo: $page"
    echo
done

echo "📊 Atualização concluída!"
