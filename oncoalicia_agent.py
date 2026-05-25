#!/usr/bin/env python3
"""
OncoAlícia · Agent de Nutrició Oncològica
==========================================
Agent conversacional basat en Claude (Anthropic) que ofereix
recomanacions nutricionals i receptes de oncoalicia.com
adaptades a la patologia i símptomes del pacient.

Requeriments:
    pip install anthropic

Ús:
    python oncoalicia_agent.py
    o bé amb clau d'API:
    ANTHROPIC_API_KEY=sk-... python oncoalicia_agent.py
"""

import os
import sys
import textwrap

try:
    import anthropic
except ImportError:
    print("Cal instal·lar la llibreria anthropic: pip install anthropic")
    sys.exit(1)

# ============================================================
# BASE DE CONEIXEMENT ONCOALÍCIA
# ============================================================
KNOWLEDGE_BASE = """
# OncoAlícia – Base de coneixement nutricional oncològic

## QUI SOM
OncoAlícia és un projecte de la Fundació Alícia (en col·laboració amb hospitals de referència
i promogut per la Fundació Catalunya La Pedrera) que proporciona recomanacions d'alimentació
i receptes adaptades a pacients en tractament oncològic.
Web: https://oncoalicia.com/receptes/

---

## TIPUS DE CÀNCER QUE COBREIX

### Càncer de cap i coll (Cabeza y cuello)
- Símptomes freqüents: nàusees, disfàgia, mucositis, pèrdua de gana, pèrdua de pes
- Informació: https://oncoalicia.com/es/tipos-de-cancer/cabeza-y-cuello/

### Càncer de pulmó (Pulmón)
- Símptomes freqüents: nàusees, pèrdua de gana, pèrdua de pes, fatiga
- Informació: https://oncoalicia.com/es/tipos-de-cancer/pulmon/

### Càncer de mama (Mama)
- Símptomes freqüents: nàusees i vòmits, pèrdua de gana, augment de pes, pèrdua de pes
- Informació: https://oncoalicia.com/es/tipos-de-cancer/mama/

### Càncer gàstric / estómac (Gástrico)
- Símptomes freqüents: nàusees, pèrdua de gana, pèrdua de pes, disfàgia, síndrome de dumping
- Pre-cirurgia: alimentació variada, equilibrada i rica en proteïnes
- Post-cirurgia: àpats petits i freqüents, evitar líquids durant els àpats
- Informació: https://oncoalicia.com/es/tipos-de-cancer/gastrico/

### Càncer colorrectal (Colorrectal)
- Símptomes freqüents: nàusees, pèrdua de gana, mucositis, flatulències, diarrea, restrenyiment
- Informació: https://oncoalicia.com/es/tipos-de-cancer/colorrectal/

### Càncer de pròstata (Próstata)
- Símptomes freqüents: flatulències, hipertensió, augment de pes
- Informació: https://oncoalicia.com/es/tipos-de-cancer/prostata/

---

## RECOMANACIONS PER SIMPTOMA

### Nàusees i vòmits
- Menja petites porcions cada 2-3 hores en lloc de grans àpats
- Prefereix aliments freds o a temperatura ambient (produeixen menys olor)
- Evita aliments grassos, molt especiats o d'olor forta
- Beu líquids freds a petits glops, sempre fora dels àpats
- Reposa assegut/da després de menjar (no tombat/da)
- El gingebre pot ajudar: en infusió, galetes o càpsules
- Receptes recomanades: Crema de patata, Polo d'albercoc i camamilla, Triturat de fruita natural, Tabulé
- Més info: https://oncoalicia.com/es/efectos-secundarios/nauseas-y-vomitos/

### Dificultat per empassar (Disfàgia)
- Adapta la textura dels aliments a la teva capacitat de deglució
- Per a sòlids: guisats, sopes, cremes, flams, purins, iogurts, fruites madures
- Humiteja els aliments amb salses, brous o oli
- Menja a poc a poc, en ambient tranquil i sense presses
- Mantén l'esquena recta mentre menges
- Evita mesclar textures molt diferents en el mateix mos
- Receptes recomanades: Crema de patata, Púding de verdura escalivada, Triturat de fruita natural, Polo d'albercoc i camamilla
- Més info: https://oncoalicia.com/es/tipos-de-cancer/cabeza-y-cuello/dificultad-para-deglutir/

### Mucositis (llagues a la boca o gola)
- Tria aliments de textura tova i suau
- Evita àcids (cítrics, tomàquet, vinagre), picants, salats o molt calents
- Prefereix aliments freds o temperats: gelats, batuts, purins
- Mantén una higiene bucal acurada amb gàrgares d'aigua bicarbonada
- Humiteja els aliments amb oli suau, salses o brou
- Menja quantitats petites i molt freqüents
- Receptes recomanades: Polo d'albercoc i camamilla, Púding de verdura escalivada, Crema de patata, Triturat de fruita natural
- Més info: https://oncoalicia.com/es/tipos-de-cancer/colorrectal/llagas-en-boca-y-o-garganta/

### Pèrdua de gana
- Fes àpats freqüents i petits (6-8 al dia)
- Aprofita els moments de més gana per menjar més
- Enriqueix els plats: oli, llet en pols, fruita seca, formatge ratllat
- Presenta els plats de manera atractiva i en ambient agradable
- Beu líquids fora dels àpats per no saciar-te
- Prioritza aliments proteics: ous, peix, carn, llegums, lactis
- Receptes recomanades: Minisandvitxos de salmó, Conill amb pinya en almívar, Papillota de peix blanc amb xampinyons, Pa fàcil de llegums
- Més info: https://oncoalicia.com/es/tipos-de-cancer/colorrectal/perdida-del-apetito/

### Pèrdua de pes
- Enriqueix tots els plats amb oli, formatge ratllat, llet en pols, fruita seca picada
- Tria aliments rics en proteïnes i energia: ous, peix, carn, llegums, lactis
- Fes 6-8 àpats petits al dia
- Pren batuts o begudes enriquides entre àpats
- Consulta amb el teu dietista-nutricionista sobre suplements nutricionals
- Receptes recomanades: Minisandvitxos de salmó, Conill amb pinya en almívar, Pa fàcil de llegums, Papillota de peix blanc amb xampinyons

### Augment de pes
- Segueix una dieta variada, equilibrada i moderada en calories
- Augmenta el consum de verdures, fruites i cereals integrals
- Redueix greixos saturats, sucres i ultraprocassats
- Beu 1,5-2 litres d'aigua al dia
- Fes activitat física moderada adaptada al teu estat
- Evita l'alcohol i les begudes ensucrades
- Receptes recomanades: Tabulé, Triturat de fruita natural, Púding de verdura escalivada
- Més info: https://oncoalicia.com/es/tipos-de-cancer/mama/aumento-de-peso/

### Flatulències i gasos
- Evita aliments que produeixen gasos: col, coliflor, bròquil, ceba, llegums en excés
- Menja a poc a poc i mastega bé per no empassar aire
- Evita begudes carbonatades
- Prefereix coccions suaus: bullir, vapor, forn
- El iogurt natural ajuda la flora intestinal
- Passeja una mica després dels àpats
- Receptes recomanades: Tabulé, Papillota de peix blanc amb xampinyons
- Més info: https://oncoalicia.com/es/tipos-de-cancer/prostata/flatulencias/

### Hipertensió
- Redueix el consum de sal: usa herbes i espècies per donar sabor
- Evita embotits, conserves, snacks salats i formatges curats
- Augmenta el consum de fruites i verdures (riques en potassi)
- Usa oli d'oliva com a greix principal
- Mantén el pes dins dels límits saludables
- Evita l'alcohol
- Receptes recomanades: Tabulé, Papillota de peix blanc amb xampinyons, Púding de verdura escalivada
- Més info: https://oncoalicia.com/es/tipos-de-cancer/prostata/hipertension/

### Diarrea
- Pren aliments astringents: arròs cuit, pastanaga cuita, poma rostida, plàtan madur
- Evita fibra insoluble: cereals integrals, verdures crues, fruites amb pell
- Beu abundants líquids per evitar la deshidratació
- Evita lactis si hi ha intolerància transitòria a la lactosa
- Prefereix coccions suaus: bullir, vapor, planxa sense greix
- Menja petites quantitats i amb freqüència
- Receptes recomanades: Crema de patata, Triturat de fruita natural

### Restrenyiment
- Augmenta el consum de fibra: fruites, verdures, cereals integrals, llegums
- Beu almenys 8 gots d'aigua al dia
- El kiwi en dejú pot activar el trànsit intestinal
- Fes activitat física moderada si el teu estat ho permet
- Pren iogurt natural per a la flora intestinal
- Evita el sedentarisme: petites passejades ajuden
- Receptes recomanades: Pa fàcil de llegums, Tabulé, Triturat de fruita natural

### Fatiga i astènia
- Prioritza aliments rics en ferro: carn vermella magra, llegums, verdures de fulla verda
- Pren vitamina C junt amb aliments rics en ferro per millorar l'absorció
- Mantén una bona hidratació
- Fes àpats petits i freqüents per mantenir l'energia estable
- Descansa prou i adapta l'activitat física al teu estat
- Receptes recomanades: Conill amb pinya en almívar, Minisandvitxos de salmó, Pa fàcil de llegums

### Síndrome de dumping (post-gastrectomia)
- Fes 6-8 àpats petits al dia
- Evita líquids durant i just després dels àpats (espera 30 min)
- Evita aliments molt ensucrats: sucs, dolços, begudes ensucrades
- Augmenta la ingesta de proteïnes i greixos saludables
- Menja a poc a poc i mastega molt bé
- Reposa tombat/da 20-30 min després de cada àpat
- Receptes recomanades: Papillota de peix blanc amb xampinyons, Púding de verdura escalivada
- Més info: https://oncoalicia.com/es/tipos-de-cancer/gastrico/tras-el-alta-hospitalaria-postcirugia/sindrome-dumping-sindrome-de-evacuacion-rapida/

---

## RECEPTES DISPONIBLES A ONCOALÍCIA

1. **Papillota de peix blanc amb salsa de xampinyons**
   - Ingredients: 150g filet de lluç, llimona, oli d'oliva, mantequilla, ceba, all, xampinyons, llet
   - Ideal per: pèrdua de gana, pèrdua de pes, hipertensió, flatulències
   - URL: https://oncoalicia.com/receptes/papillote-de-pescado-blanco-con-salsa-de-champinones/

2. **Crispetes condimentades (Palomitas)**
   - Ingredients: 30g blat de moro per crispetes, oli d'oliva, sal, espècies (gingebre, llimona, orenga, pebre vermell, canyella, ratlladura de taronja)
   - Ideal per: pèrdua de gana (snack nutritiu)
   - URL: https://oncoalicia.com/receptes/palomitas-condimentadas/

3. **Tabulé**
   - Ingredients: 60g cuscús precuit, mig tomàquet, mitja ceba tendra, julivert, coriandre, suc de llimona, oli d'oliva
   - Ideal per: augment de pes, flatulències, hipertensió, restrenyiment
   - URL: https://oncoalicia.com/receptes/tabule/

4. **Conill amb pinya en almívar**
   - Ingredients: 125g conill tallat a trossos, ceba, 2 rodanxes de pinya en almívar, oli d'oliva, canyella en branca
   - Ideal per: pèrdua de gana, pèrdua de pes, fatiga
   - URL: https://oncoalicia.com/receptes/conejo-con-pina-en-almibar/

5. **Pa fàcil de llegums**
   - Ingredients: 200g llenties seques, 60g aigua, 25g oli d'oliva, 4g llevat químic, sal, herbes aromàtiques opcionals
   - Ideal per: pèrdua de gana, pèrdua de pes, restrenyiment, fatiga
   - URL: https://oncoalicia.com/receptes/pa-facil-de-llegums/

6. **Crema de patata**
   - Ingredients: 200g llet desnatada, 30g flocs de patata, 20g oli d'oliva, 15g llet en pols desnatada, sal
   - Ideal per: nàusees, disfàgia, mucositis, diarrea
   - URL: https://oncoalicia.com/receptes/crema-de-patata/

7. **Púding de verdura escalivada**
   - Ingredients: 150g verdures rostides (escalivades), 1 ou, 50ml nata líquida
   - Ideal per: disfàgia, mucositis, augment de pes, hipertensió, dumping
   - URL: https://oncoalicia.com/receptes/pudin-de-verdura-asada/

8. **Polo d'albercoc i camamilla**
   - Ingredients: 5 albercocs madurs, 100ml infusió de camamilla, ratlladura de taronja (opcional)
   - Ideal per: nàusees, mucositis (efecte calmant i refrescant)
   - URL: https://oncoalicia.com/receptes/polo-dalbercoc-i-camamilla/

9. **Minisandvitxos de salmó**
   - Ingredients: pa de motlle, salmó, cogombre, tomàquet, formatge crema, oli d'oliva
   - Ideal per: pèrdua de gana, pèrdua de pes, fatiga
   - URL: https://oncoalicia.com/receptes/minisandwiches-sandwich-de-salmon/

10. **Triturat de fruita natural**
    - Ingredients: préssec, pera, mango, kiwi, meló o altres fruites al gust
    - Ideal per: nàusees, disfàgia, mucositis, pèrdua de gana, augment de pes, diarrea, restrenyiment
    - URL: https://oncoalicia.com/receptes/triturado-de-fruta-natural/

---

## RECOMANACIONS GENERALS
- Consulta SEMPRE el teu equip mèdic i/o dietista-nutricionista davant de qualsevol dubte
- Les recomanacions s'han d'adaptar a cada persona, situació i moment del tractament
- Les receptes d'OncoAlícia NO substitueixen el tractament mèdic
- Web general: https://oncoalicia.com/es/recomendaciones-generales/
- Totes les receptes: https://oncoalicia.com/receptes/
"""

SYSTEM_PROMPT = f"""Ets l'agent de nutrició d'**OncoAlícia**, una iniciativa de la Fundació Alícia per ajudar pacients oncològics a alimentar-se millor durant el tractament del càncer.

La teva missió és:
1. Preguntar per la **patologia del pacient** (tipus de càncer o diagnòstic) si no es coneix
2. Preguntar pels **símptomes o efectes secundaris** del tractament
3. Oferir **recomanacions nutricionals personalitzades** i **receptes específiques** d'OncoAlícia
4. Proporcionar els **enllaços web** d'OncoAlícia rellevants per a cada situació

IMPORTANT - Regles de comportament:
- Detecta l'idioma de l'usuari i respon SEMPRE en el mateix idioma (català o castellà)
- Si l'usuari escriu en castellà, respon en castellà. Si escriu en català, respon en català
- MAI no facis diagnòstics mèdics ni prescripcions
- SEMPRE recorda que les recomanacions no substitueixen el consell mèdic professional
- Sigues proper/a, empàtic/a i comprensiu/va amb el pacient
- Dona recomanacions concretes i pràctiques basades en la base de coneixement
- Quan suggereixis receptes, inclou sempre l'URL de la recepta d'OncoAlícia
- Si no saps la resposta, deriva l'usuari a oncoalicia.com o al seu equip mèdic
- Mantén les respostes clares, estructurades i fàcils de llegir
- Usa emojis amb moderació per fer les respostes més amigables

BASE DE CONEIXEMENT:
{KNOWLEDGE_BASE}

Comença la conversa presentant-te i preguntant per la patologia del pacient.
"""

# ============================================================
# UTILS
# ============================================================
def print_separator(char="─", width=60):
    print(char * width)

def print_bot(text: str):
    print("\n🥗 OncoAlícia:")
    print_separator()
    # Wrap long lines
    for line in text.split("\n"):
        if line.strip():
            wrapped = textwrap.fill(line, width=70, subsequent_indent="   ")
            print(wrapped)
        else:
            print()
    print_separator()
    print()

def print_welcome():
    print_separator("═")
    print("  🥗  OncoAlícia · Agent de Nutrició Oncològica")
    print("       Fundació Alícia · oncoalicia.com")
    print_separator("═")
    print("  ℹ️  Escriu 'sortir' o 'salir' per acabar la sessió")
    print("  ℹ️  L'agent respon en català o castellà automàticament")
    print_separator("═")
    print()

# ============================================================
# MAIN AGENT
# ============================================================
def run_agent():
    # Get API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  No s'ha trobat la clau d'API d'Anthropic.")
        print("   Defineix la variable d'entorn ANTHROPIC_API_KEY:")
        print("   export ANTHROPIC_API_KEY=sk-ant-...")
        api_key = input("\n   O introdueix la clau aquí: ").strip()
        if not api_key:
            print("❌ No s'ha proporcionat cap clau d'API. Sortint.")
            sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    conversation_history = []
    model = "claude-sonnet-4-6"

    print_welcome()

    # Initial greeting from the bot
    print("🔄 Iniciant l'agent...")
    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": "Inicia la conversa presentant-te i preguntant per la patologia del pacient."
            }]
        )
        bot_greeting = response.content[0].text
        # Add to history as if bot started
        conversation_history.append({
            "role": "user",
            "content": "Inicia la conversa presentant-te i preguntant per la patologia del pacient."
        })
        conversation_history.append({
            "role": "assistant",
            "content": bot_greeting
        })
        print_bot(bot_greeting)
    except anthropic.AuthenticationError:
        print("❌ Clau d'API incorrecta. Comprova la teva ANTHROPIC_API_KEY.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error en connectar amb l'API: {e}")
        sys.exit(1)

    # Conversation loop
    while True:
        try:
            user_input = input("👤 Tu: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Sessió finalitzada. Que et recuperis aviat!")
            break

        if not user_input:
            continue

        if user_input.lower() in ('sortir', 'salir', 'exit', 'quit', 'adeu', 'adiós', 'bye'):
            print("\n👋 Gràcies per usar OncoAlícia. Que et recuperis aviat! / ¡Gracias por usar OncoAlícia. ¡Que te recuperes pronto!")
            break

        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        try:
            print("\n⏳ Pensant...")
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=conversation_history
            )
            bot_response = response.content[0].text

            # Add bot response to history
            conversation_history.append({
                "role": "assistant",
                "content": bot_response
            })

            print_bot(bot_response)

            # Keep conversation history manageable (last 20 messages)
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]

        except anthropic.RateLimitError:
            print("\n⚠️  S'ha superat el límit de sol·licituds. Espera un moment i torna-ho a intentar.")
        except anthropic.APIError as e:
            print(f"\n❌ Error de l'API: {e}")
        except Exception as e:
            print(f"\n❌ Error inesperat: {e}")


if __name__ == "__main__":
    run_agent()
