#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Common functions

debugMe = False

def uniq(values):
    output = []
    seen = set()
    for value in values:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

def lower_capitalized(input):
    newString = input.lower().replace(u"/", u" / ").replace(u".", u". ").replace(u"-", u" - ")
    toOutput = []
    for s in newString.split(u" "):
        tmp = s.capitalize()
        toOutput.append(tmp)
    newString = u" ".join(toOutput)
    output = newString.replace(u" Da ", u" da ").replace(u" Das ", u" das ").replace(u" De ", u" de ").replace(u" Do ", u" do ").replace(u" Dos ", u" dos ").replace(u" E ", u" e ").replace(u" X ", u" x ").replace(u" Via ", u" via ").replace(u"  ", u" ").replace(u"ª", u"ª ").replace(u"  ", u" ").replace(u"  ", u" ")
    # Specific place names
    output = output.replace(u"Br101", u"BR-101")
    output = output.replace(u"Br 101", u"BR-101")
    output = output.replace(u"Br 262", u"BR-262")
    output = output.replace(u"Es 010", u"ES-010")
    output = output.replace(u"(bike Gv)", u"(Bike GV)")
    output = output.replace(u"circular", u"Circular")
    output = output.replace(u"Parq.", u"Parque")
    output = output.replace(u"Exp.", u"Expedito")
    output = output.replace(u"Expd.", u"Expedito")
    output = output.replace(u"Beira M", u"Beira Mar").replace(u"Beira Marar", u"Beira Mar")
    output = output.replace(u"B. Mar", u"Beira Mar")
    output = output.replace(u"S. Dourada", u"Serra Dourada")
    output = output.replace(u"Iii", u"III")
    output = output.replace(u"Ii", u"II")
    output = output.replace(u"Jacaraipe", u"Jacaraípe")
    output = output.replace(u"Rodoviaria", u"Rodoviária")
    output = output.replace(u"P. Costa", u"Praia da Costa")
    output = output.replace(u"J. Camburi", u"Jardim Camburi")
    output = output.replace(u"M. Noronha", u"Marcilio de Noronha")
    output = output.replace(u"M. de Noronha", u"Marcilio de Noronha")
    output = output.replace(u"C. Itaperica", u"Condominio Itaparica")
    output = output.replace(u"P. Itapoã", u"Praia de Itapoã")
    output = output.replace(u"T . ", u"T. ")
    output = output.replace(u"T.", u"Terminal")
    output = output.replace(u"T Laranjeiras", u"Terminal Laranjeiras")
    output = output.replace(u"Itaciba", u"Utacibá")
    output = output.replace(u"Jacaraipe", u"Jacaraípe")
    output = output.replace(u"Pç", u"Praça")
    output = output.replace(u"Av.", u"Avenida")
    output = output.replace(u"Av ", u"Avenida ")
    output = output.replace(u"Torquatro", u"Torquato")
    output = output.replace(u"S. Torquato", u"São Torquato")
    output = output.replace(u"Darlysantos", u"Darly Santos")
    output = output.replace(u"Col. Laranjeiras", u"Colina de Laranjeiras")
    output = output.replace(u"Mal.", u"Marechal")
    output = output.replace(u"B. República", u"Bairro República")
    output = output.replace(u"B. Ipanema", u"Bairro Ipanema")
    output = output.replace(u"B. Primavera", u"Bairro Primavera")
    output = output.replace(u"V. Bethânia", u"Vila Bethânia")
    output = output.replace(u"V. Encantado", u"Vale Encantado")
    output = output.replace(u"Heac", u"HEAC")
    output = output.replace(u"B. Carapebus", u"Bairro Carapebus")
    output = output.replace(u"C. Continental", "Cidade Continental")
    output = output.replace(u"S. Mônica", u"Santa Mônica")
    output = output.replace(u"R. Penha", u"Reta da Penha")
    output = output.replace(u"Paulo P. Gomes", u"Paulo Pereira Gomes")
    output = output.replace(u"C. Itaparica", u"Coqueiral de Itaparica")
    output = output.replace(u"C. Verde", u"Campo Verde")
    output = output.replace(u"P. Cariacica", u"Porto de Cariacica")
    output = output.replace(u"A. Ramos", u"Alzira Ramos")
    output = output.replace(u"Afb", "A. F. Borges")
    output = output.replace(u"A. F. Borges", "Antonio Ferreira Borges")
    output = output.replace(u"3º", u"3ª")
    output = output.replace(u"Norte/sul", u"Norte Sul")
    output = output.replace(u"Norte / Sul", u"Norte Sul")
    output = output.replace(u"Norte-sul", u"Norte Sul")
    output = output.replace(u"J. Penha", u"Jardim da Penha")
    output = output.replace(u"J. América", u"Jardim América")
    output = output.replace(u"J. America", u"Jardim América")
    output = output.replace(u"J. Marilândia", u"Jardim Marilândia")
    output = output.replace(u"Rod.", u"Rodovia")
    output = output.replace(u"Res.", u"Residencial")
    output = output.replace(u"Cdp", u"CDP")
    output = output.replace(u"Crefes", u"CREFES")
    output = output.replace(u"Ceasa", u"CEASA")
    output = output.replace(u"Ifes", u"IFES")
    output = output.replace(u"Civit", u"CIVIT")
    output = output.replace(u"V. N.", u"Vila Nova")
    output = output.replace(u"Psme", u"PSME")
    output = output.replace(u"Bl.", u"Balneário")
    output = output.replace(u"B - C - A", u"B-C-A")
    output = output.replace(u"(expresso)", u"- Expresso")
    output = output.replace(u"D`água", u"d`Água")
    output = output.replace(u"Hosp.", u"Hospital")
    return output.strip()

def debug_to_screen(text, newLine=True):
    if debugMe:
        if newLine:
            print text
        else:
            print text,

