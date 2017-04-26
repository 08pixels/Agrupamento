# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from django.db import connection, transaction
from django.db.transaction import commit
from django.shortcuts import render, redirect, get_object_or_404

import numpy as np
from scipy.cluster.vq import kmeans, vq
from pylab import plot,show

from programacao.forms import EspecialistaForm, RegistroForm, UserEditForm, AvaliacaoEspecialistaForm, ProblemaForm, CriterioEspecialistaForm
from programacao.models import Problema, Codigo, Especialista, AvaliacaoEspecialista, Agrupamento, AvaliacaoAgrupamento, Similaridade, CriterioEspecialista

from radon.raw import analyze
from radon.metrics import mi_visit
from radon.metrics import mi_compute
from radon.metrics import h_visit
from radon.complexity import cc_visit
from radon.cli.tools import iter_filenames
from radon.mccabe_complexity import ciclomatic_complexity

from radon.similarity import edit
from radon.similarity import tag
from radon.similarity import tree

from utils import *

import os
import re
import sys
import utils
import shutil

def index(request, template_name='programacao/index.html'):
    if request.method=='POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            u = form.get_user()
            login(request, u)
            if u.has_perm('programacao.view_especialista'):
                return redirect(reverse(viewname='programacao:especialista_index'))
        else: 
            messages.add_message(request, messages.ERROR, 'Usuário não cadastrado ou sem permissão de acesso!')

    form = AuthenticationForm()

    data = {}
    data['form'] = form
    return render(request, template_name, data)


def registro(request, template_name='programacao/registro.html'):
    if request.method == 'POST':
        especialista_form = EspecialistaForm(request.POST or None)
        user_form = RegistroForm(request.POST or None)
        if especialista_form.is_valid() and user_form.is_valid():
            with transaction.atomic():
                user = user_form.save(commit=False)
                user.is_active = True
                user.save()
 
                especialista = especialista_form.save(commit=False)
                especialista.user = user
                especialista.save()

                permission = Permission.objects.get(name='view_especialista')
                user.user_permissions.add(permission)

                messages.add_message(request, messages.INFO, 'Cadastro realizado com sucesso!')
                return redirect('programacao:index')
        else:
            messages.add_message(request, messages.ERROR, 'Erro ao tentar cadastrar!') 

    especialista_form = EspecialistaForm()
    user_form = RegistroForm()

    data = {}
    data['especialista_form'] = especialista_form
    data['user_form'] = user_form
    return render(request, template_name, data)


def sair(request):
    logout(request)
    return redirect('programacao:index')


@login_required
@permission_required('programacao.view_autor')
def admin_index(request, template_name='programacao/admin_index.html'):
    problemas = Problema.objects.all()
    problemas_publicados = Problema.objects.filter(publicar=True)

    problemas_count = Problema.objects.count()
    submissoes_count = Codigo.objects.count()
    avaliacoes_realizadas_count = AvaliacaoEspecialista.objects.count()

    count_avaliacoes_pendentes = 0
    problema_submissoes_linguagem = {} 
    for problema in problemas:
        count_avaliacoes_pendentes = count_avaliacoes_pendentes + problema.get_count_avaliacoes_pendentes()
        results = list(query_to_dicts(u"SELECT p.id, l.name as language, COUNT(s.id) as qtd FROM huxley.problem as p, huxley.submission as s, huxley.language as l WHERE p.id = s.problem_id AND p.id = %d AND l.id = s.language_id GROUP BY l.name" % problema.id ))
        lings = [0,0,0,0] #c, python2, python3, outra
        for row in results :
            language = row['language']
            qtd = row['qtd']
            if language == 'C' :
                lings[0] = qtd
            elif language == 'Python' :
                lings[1] = qtd
            elif language == 'Python3.2' :
                lings[2] = qtd
            else :
                lings[3] += qtd
        problema_submissoes_linguagem[problema.id] = tuple(lings)

    data = {}
    data['problemas_list'] = problemas
    data['problemas_publicados_list'] = problemas_publicados
    data['count_problemas'] = problemas_count
    data['count_submissoes'] = submissoes_count
    data['count_avaliacoes_realizadas'] = avaliacoes_realizadas_count
    data['count_avaliacoes_pendentes'] = (count_avaliacoes_pendentes - avaliacoes_realizadas_count)
    data['problema_submissoes_linguagem'] = problema_submissoes_linguagem 
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_importar_problemas(request, template_name='programacao/admin_index.html'):
    results = list(query_to_dicts(u"SELECT id, name, description, input_format, output_format FROM huxley.problem WHERE name is not NULL AND name != '' AND description is not NULL AND description != '' AND input_format is not NULL AND input_format != '' AND output_format is not NULL AND output_format != ''"))

    for row in results :
        nome = remove_acentos(row['name'])
        id_huxley = row['id']
        enunciado = remove_acentos(row['description'])
        entrada = remove_acentos(row['input_format'])
        saida = remove_acentos(row['output_format'])

        dirsrc = os.path.jogerar/similaridades/problema/65in(settings.MEDIA_ROOT, 'submissions')
        dirsrc = os.path.join(dirsrc, str(id_huxley))
        if (os.path.exists(dirsrc)):
            Problema.objects.create(nome=nome, id_huxley=id_huxley, enunciado=enunciado, entrada=entrada, saida=saida)

    problemas = Problema.objects.all()
    problemas_publicados = Problema.objects.filter(publicar=True)
    problemas_count = Problema.objects.count()
    submissoes_count = Codigo.objects.count()
    avaliacoes_realizadas_count = AvaliacaoEspecialista.objects.count()

    count_avaliacoes_pendentes = 0
    for problema in problemas:
        count_avaliacoes_pendentes = count_avaliacoes_pendentes + problema.get_count_avaliacoes_pendentes()

    data = {}
    data['problemas_list'] = problemas
    data['problemas_publicados_list'] = problemas_publicados
    data['count_problemas'] = problemas_count
    data['count_submissoes'] = submissoes_count
    data['count_avaliacoes_realizadas'] = avaliacoes_realizadas_count
    data['count_avaliacoes_pendentes'] = (count_avaliacoes_pendentes - avaliacoes_realizadas_count)
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_editar_problema(request, pk, template_name='programacao/admin_editar_problema.html'):
    problema = get_object_or_404(Problema, pk=pk)

    form = ProblemaForm(request.POST or None, instance=problema)

    if form.is_valid():
        form.save()
        return redirect('programacao:admin_editar_problema', pk)
    
    data = {}
    data['form'] = form
    data['problema'] = problema
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_problema_submissoes(request, pk, template_name='programacao/admin_problema_submissoes.html'):
    problema = get_object_or_404(Problema, pk=pk)

    turma_submissoes_linguagem = {}
    results_turmas = list(query_to_dicts(u"SELECT c.id, c.name as turma FROM huxley.user as u, huxley.user_role as ur, huxley.role as r, huxley.user_cluster as uc, huxley.cluster as c, huxley.submission as s, huxley.problem as p WHERE u.id = ur.user_id AND ur.role_id = r.id AND r.authority = 'ROLE_STUDENT' AND u.id = uc.user_id AND uc.cluster_id = c.id AND s.user_id = u.id AND s.problem_id = p.id AND p.id = %d AND u.id NOT IN (SELECT u.id FROM huxley.user as u, huxley.user_role as ur, huxley.role as r, huxley.user_cluster as uc, huxley.cluster as c WHERE u.id = ur.user_id AND ur.role_id = r.id AND r.authority = 'ROLE_TEACHER' AND u.id = uc.user_id AND uc.cluster_id = c.id) GROUP BY c.id, c.name ORDER BY c.name" % problema.id_huxley))
    for row_turma in results_turmas :
        id = row_turma['id']
        row_turma['turma'] = remove_acentos(row_turma['turma'])
        results = list(query_to_dicts(u"SELECT c.id as id, c.name as turma, l.name as linguagem, COUNT(l.id) as qtd FROM huxley.user as u, huxley.user_role as ur, huxley.role as r, huxley.user_cluster as uc, huxley.cluster as c, huxley.submission as s, huxley.problem as p, huxley.language as l WHERE u.id = ur.user_id AND ur.role_id = r.id AND r.authority = 'ROLE_STUDENT' AND u.id = uc.user_id AND uc.cluster_id = c.id AND c.id = %d AND s.user_id = u.id AND s.problem_id = p.id AND l.id = s.language_id AND p.id = %d AND u.id NOT IN (SELECT u.id FROM huxley.user as u, huxley.user_role as ur, huxley.role as r, huxley.user_cluster as uc, huxley.cluster as c WHERE u.id = ur.user_id AND ur.role_id = r.id AND r.authority = 'ROLE_TEACHER' AND u.id = uc.user_id AND uc.cluster_id = c.id AND c.id = %d) GROUP BY c.id, c.name, l.name ORDER BY c.name" % (id, problema.id_huxley, id)))
        lings = [0,0,0,0] # c, python2, python3, outra
        for row in results :
            language = row['linguagem']
            qtd = row['qtd']
            if language == 'C' :
                lings[0] = qtd
            elif language == 'Python' :
                lings[1] = qtd
            elif language == 'Python3.2' :
                lings[2] = qtd
            else :
                lings[3] += qtd
        turma_submissoes_linguagem[id] = tuple(lings)

    problemas = Problema.objects.all()
    problemas_publicados = Problema.objects.filter(publicar=True)
    problemas_count = Problema.objects.count()
    submissoes_count = Codigo.objects.count()
    avaliacoes_realizadas_count = AvaliacaoEspecialista.objects.filter().count()

    count_avaliacoes_pendentes = 0
    for p in problemas:
        count_avaliacoes_pendentes = count_avaliacoes_pendentes + p.get_count_avaliacoes_pendentes()

    data = {}
    data['results'] = results_turmas
    data['turma_submissoes_linguagem'] = turma_submissoes_linguagem
    data['problema'] = problema
    data['problemas_list'] = problemas
    data['problemas_publicados_list'] = problemas_publicados
    data['count_problemas'] = problemas_count
    data['count_submissoes'] = submissoes_count
    data['count_avaliacoes_realizadas'] = avaliacoes_realizadas_count
    data['count_avaliacoes_pendentes'] = (count_avaliacoes_pendentes - avaliacoes_realizadas_count)
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_importar_submissoes_turma(request, pk1, pk2, template_name='programacao/especialista_visualizar_problema.html'):
    problema = get_object_or_404(Problema, pk=pk1)
    id_turma = int(pk2)

    # determina turma principal (aquela que sera avaliada pelos especialistas)
    if (problema.id_turma_principal == None) :
        problema.id_turma_principal = id_turma
        problema.save()

    importar = Codigo.objects.filter(problema=problema, id_turma=id_turma)
    # não importar os códigos de uma turma mais de uma vez
    if not(importar) :
        results = list(query_to_dicts(u"SELECT p.id as problem, s.user_id as user, l.name as language, s.tries as tries, s.submission as file, s.evaluation as corretude FROM huxley.user as u, huxley.user_role as ur, huxley.role as r, huxley.user_cluster as uc, huxley.cluster as c, huxley.submission as s, huxley.problem as p, huxley.language as l WHERE u.id = ur.user_id AND ur.role_id = r.id AND r.authority = 'ROLE_STUDENT' AND u.id = uc.user_id AND uc.cluster_id = c.id AND c.id = %s AND s.user_id = u.id AND s.problem_id = p.id AND l.id = s.language_id AND p.id = %s AND u.id NOT IN (SELECT u.id FROM huxley.user as u, huxley.user_role as ur, huxley.role as r, huxley.user_cluster as uc, huxley.cluster as c WHERE u.id = ur.user_id AND ur.role_id = r.id AND r.authority = 'ROLE_TEACHER' AND u.id = uc.user_id AND uc.cluster_id = c.id AND c.id = %s)" %(id_turma, problema.id_huxley, id_turma)) )

        count = 1
        for row in results :
            problem = row['problem']
            user = row['user']
            language = row['language']
            tries = row['tries']
            filesrc = remove_acentos(row['file'])
            codigo_corretude = row['corretude']
            tupla_corretude = corretude(codigo_corretude)
            # problem id, user id, language, tries, file (submission)
            dirsrc = os.path.join(settings.MEDIA_ROOT, 'submissions')
            dirsrc = os.path.join(dirsrc, str(problem), str(user), str(language), str(tries))
            # verifica se existe diretório fonte
            if (os.path.exists(dirsrc)):
                dirsrc = os.path.join(dirsrc, str(filesrc))
                # verifica se existe arquivo fonte
                if (os.path.exists(dirsrc)):
                    remove_comments_main(dirsrc, language)
                    # cria diretório destino
                    dirdest = os.path.join(settings.MEDIA_ROOT, 'codigos')
                    dirdest = os.path.join(dirdest, str(problem))
                    if not(os.path.exists(dirdest)):
                        os.mkdir(dirdest)
                    dirdest = os.path.join(dirdest, str(id_turma))
                    if not(os.path.exists(dirdest)):
                        os.mkdir(dirdest)
                    # determina linguagem
                    language = select_language(language)
                    extensao = select_extensao(language)
                    # nome do arquivo
                    arquivo = "sol" + str(id_turma) + str(count) + extensao
                    dirdest = os.path.join(dirdest, arquivo)
                    # copia arquivo
                    shutil.copy2(dirsrc+".nocomments", dirdest)
                    count += 1
                    try:
                        # extracao de metricas
                        with open(dirdest) as fobj:
                            source = fobj.read()
                        # ciclomatic_ complexity
                        complexity = 0
                        try :
                            complexity = ciclomatic_complexity(dirdest)
                        except :
                            complexity = 0
                        # Raw metrics
                        raw = analyze(source)
                        # Halstead metrics
                        halstead = h_visit(source)
                        # raw metrics                   
                        LOC = raw[0]  # raw metrics
                        LLOC = raw[1] # raw metrics
                        SLOC = raw[2] # raw metrics
                        comments = raw[3] # raw metrics
                        multi = raw[4] # raw metrics
                        blank = raw[5] # raw metrics
                        single_comments = raw[6] # raw metrics
                        # halstead metrics
                        number_distinct_operators = halstead[0] # halstead metrics
                        number_distinct_operands = halstead[1] # halstead metrics
                        total_number_operators = halstead[2] # halstead metrics
                        total_number_operands = halstead[3] # halstead metrics
                        vocabulary = halstead[4] # halstead metrics
                        length = halstead[5] # halstead metrics
                        calculated_length = halstead[6]# halstead metrics
                        volume = halstead[7] # halstead metrics
                        difficulty = halstead[8] # halstead metrics
                        effort = halstead[9] # halstead metrics
                        time = halstead[10] # halstead metrics
                        bugs = halstead[11] # halstead metrics
                        # mi metric
                        mi = mi_compute(halstead[7], complexity, raw[2], raw[3]) # mi metric

                        # cria model para codigo
                        Codigo.objects.create(arquivo=arquivo, id_turma=id_turma, linguagem=language, problema=problema, medidas_ok=True, medida_corretude_funcional=tupla_corretude[0], medida_corretude_sintatica=tupla_corretude[1], medida_complexity=complexity, medida_loc=LOC, medida_lloc=LLOC, medida_sloc=SLOC, medida_comments=comments, medida_multi=multi, medida_blank=blank, medida_single_comments=single_comments, medida_distinct_operators=number_distinct_operators, medida_distinct_operands=number_distinct_operands, medida_total_number_operators=total_number_operators, medida_total_number_operands=total_number_operands, medida_vocabulary=vocabulary, medida_length=length, medida_calculated_length=calculated_length, medida_volume=volume, medida_difficulty=difficulty, medida_effort=effort, medida_time=time, medida_bugs=bugs, medida_mi=mi)
                    except :
                        # cria model para codigo
                        Codigo.objects.create(arquivo=arquivo, id_turma=id_turma, linguagem=language, problema=problema, medidas_ok=False, medida_corretude_funcional=tupla_corretude[0], medida_corretude_sintatica=tupla_corretude[1])

    codigos_list = Codigo.objects.filter(problema=problema)
    avaliacao_list = AvaliacaoEspecialista.objects.filter(codigo__problema=problema)

    user = request.user
    especialista = Especialista.objects.get(user_id=user.id)
    criterios = None
    try:
        criterios = CriterioEspecialista.objects.get(problema=problema, especialista=especialista)
    except:
        pass
    form = CriterioEspecialistaForm(request.POST or None, instance=criterios)
    if form.is_valid():
        form.save()
        return redirect('programacao:especialista_visualizar_problema')

    data = {}
    data['form'] = form
    data['problema'] = problema
    data['codigos_list'] = codigos_list
    data['avaliacao_list'] = avaliacao_list
    return render(request, template_name, data)

@login_required
@permission_required('programacao.view_autor')
def admin_medidas(request, pk, template_name='programacao/admin_medidas.html'):
    problema = get_object_or_404(Problema, pk=pk)
    codigos_list = Codigo.objects.filter(problema=problema)

    for codigo in codigos_list:
        dirdest = ''
        try:
            dirdest = os.path.join(settings.MEDIA_ROOT, 'codigos', str(codigo.problema.id_huxley), str(codigo.id_turma), str(codigo.arquivo))
            print("Arquivo: " + dirdest)
            try:
                # extracao de metricas
                with open(dirdest) as fobj:
                    source = fobj.read()
                # ciclomatic_ complexity
                complexity = 0
                try :
                    complexity = ciclomatic_complexity(dirdest)
                except Exception as e:
                    print("Complexity Error ")
                    print(e)
                    complexity = 1
                # Raw metrics
                #raw = analyze(source)
                # raw metrics                   
                #LOC = raw[0]  # raw metrics
                #LLOC = raw[1] # raw metrics
                #SLOC = raw[2] # raw metrics
                #comments = raw[3] # raw metrics
                #multi = raw[4] # raw metrics
                #blank = raw[5] # raw metrics
                #single_comments = raw[6] # raw metrics
                # Halstead metrics
                number_distinct_operators = 0
                number_distinct_operands = 0
                try :
                    halstead = h_visit(source)
                    number_distinct_operators = halstead[0] # halstead metrics
                    number_distinct_operands = halstead[1] # halstead metrics
                    #total_number_operators = halstead[2] # halstead metrics
                    #total_number_operands = halstead[3] # halstead metrics
                    #vocabulary = halstead[4] # halstead metrics
                    #length = halstead[5] # halstead metrics
                    #calculated_length = halstead[6]# halstead metrics
                    #volume = halstead[7] # halstead metrics
                    #difficulty = halstead[8] # halstead metrics
                    #effort = halstead[9] # halstead metrics
                    #time = halstead[10] # halstead metrics
                    #bugs = halstead[11] # halstead metrics
                except Exception as e:
                    print("Halstead Error ")
                    print(e)
                    number_distinct_operators = 0
                    number_distinct_operands = 0
                # mi metric
                #mi = mi_compute(halstead[7], complexity, raw[2], raw[3]) # mi metric

                # atualiza model para codigo
                codigo.medida_complexity = complexity
                codigo.medida_distinct_operators = number_distinct_operators
                codigo.medida_distinct_operands = number_distinct_operands

                codigo.medidas_ok = True
                codigo.save()
            except Exception as e:
                print("Metrics Error ")
                print(e)
        except Exception as e:
            print("Arquivo não encontrado!")
            print(e)


    data = {}
    data['problema'] = problema
    data['codigos_list'] = codigos_list
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_testar(request, template_name='programacao/admin_testar.html'):
    problemas = Problema.objects.all()
    problemas_publicados = Problema.objects.filter(publicar=True)

    problemas_count = Problema.objects.count()
    submissoes_count = Codigo.objects.count()
    avaliacoes_realizadas_count = AvaliacaoEspecialista.objects.count()

    count_avaliacoes_pendentes = 0
    for problema in problemas:
        count_avaliacoes_pendentes = count_avaliacoes_pendentes + problema.get_count_avaliacoes_pendentes()

    data = {}
    data['problemas_list'] = problemas
    data['problemas_publicados_list'] = problemas_publicados
    data['count_problemas'] = problemas_count
    data['count_submissoes'] = submissoes_count
    data['count_avaliacoes_realizadas'] = avaliacoes_realizadas_count
    data['count_avaliacoes_pendentes'] = (count_avaliacoes_pendentes - avaliacoes_realizadas_count)
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_testar_problema_submissoes(request, pk, template_name='programacao/admin_testar_problema_submissoes.html'):
    problema = get_object_or_404(Problema, pk=pk)

    codigos_list = Codigo.objects.filter(problema=problema)

    data = {}
    data['problema'] = problema
    data['codigos_list'] = codigos_list
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_testar_submissao(request, pk, template_name='programacao/admin_testar_problema_submissoes.html'):
    codigo = get_object_or_404(Codigo, pk=pk)

    try :
        results = list(query_to_dicts(u"SELECT input as entrada, output as saida FROM huxley.test_case WHERE problem_id = %d" % (codigo.problema.id_huxley)))
        count_tests = 0
        count_failures = 0
        for row in results :
            entrada = row['entrada']
            entrada = entrada.split()
            saida = row['saida']
            count_tests += 1
            if not(testar_solucao(codigo, entrada, saida)) :
                count_failures += 1
        corretude = 100 * (count_tests - count_failures) / count_tests
        codigo.medida_corretude_funcional = corretude
        codigo.save()
    except:
        codigo.medida_corretude_funcional = 0.0 # substituir None por 0
        codigo.save()        

    problema = Problema.objects.get(id=codigo.problema.id)
    codigos_list = Codigo.objects.filter(problema=problema)

    data = {}
    data['problema'] = problema
    data['codigos_list'] = codigos_list
    return render(request, template_name, data)

@login_required
@permission_required('programacao.view_autor')
def admin_ver_similaridades(request, pk, template_name='programacao/admin_similaridades.html'):
    problemas = Problema.objects.filter(publicar=False)
    problemas_publicados = Problema.objects.filter(publicar=True)

    problemas_count = Problema.objects.count()
    submissoes_count = Codigo.objects.count()
    avaliacoes_realizadas_count = AvaliacaoEspecialista.objects.count()

    count_avaliacoes_pendentes = 0
    for p in problemas:
        count_avaliacoes_pendentes = count_avaliacoes_pendentes + p.get_count_avaliacoes_pendentes()

    problema = get_object_or_404(Problema, pk=pk)
    similaridades = Similaridade.objects.filter(codigo_referencia__problema=problema).order_by('algoritmo')

    data = {}
    data['problema'] = problema
    data['similaridades_list'] = similaridades
    data['problemas_list'] = problemas
    data['problemas_publicados_list'] = problemas_publicados
    data['count_problemas'] = problemas_count
    data['count_submissoes'] = submissoes_count
    data['count_avaliacoes_realizadas'] = avaliacoes_realizadas_count
    data['count_avaliacoes_pendentes'] = (count_avaliacoes_pendentes - avaliacoes_realizadas_count)
    return render(request, template_name, data)

@login_required
@permission_required('programacao.view_autor')
def admin_similaridades(request, pk, template_name='programacao/admin_similaridades.html'):
    problemas = Problema.objects.filter(publicar=False)
    problemas_publicados = Problema.objects.filter(publicar=True)

    problemas_count = Problema.objects.count()
    submissoes_count = Codigo.objects.count()
    avaliacoes_realizadas_count = AvaliacaoEspecialista.objects.count()

    count_avaliacoes_pendentes = 0
    for p in problemas:
        count_avaliacoes_pendentes = count_avaliacoes_pendentes + p.get_count_avaliacoes_pendentes()

    problema = get_object_or_404(Problema, pk=pk)
    submissoes = Codigo.objects.filter(problema=problema)

    dirdest = os.path.join(settings.MEDIA_ROOT, 'codigos', str(problema.id_huxley))
    try :
        '''
        cod_ref = Codigo.objects.get(id = 412)
        s1 = os.path.join(dirdest, str(submissoes[0].id_turma), cod_ref.arquivo)
        with open(s1) as fobj:
            source1 = fobj.read()
        '''
        i_values = range(0, len(submissoes)) # [27,28,29]
        for i in i_values: 
            s1 = os.path.join(dirdest, str(submissoes[i].id_turma), submissoes[i].arquivo)
            with open(s1) as fobj:
                source1 = fobj.read()

            j_values = range(i, len(submissoes)) #[27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
            for j in j_values:
                s2 = os.path.join(dirdest, str(submissoes[j].id_turma), submissoes[j].arquivo)
                with open(s2) as fobj:
                    source2 = fobj.read()

                codigo_referencia = submissoes[i]
                codigo_solucao = submissoes[j]

                if (i == j) :
                    algoritmo = "Jaccard"
                    #print("Jaccard %s(%d) %s(%d)" %(codigo_referencia.arquivo, i, codigo_solucao.arquivo, j))
                    #coeficiente_similaridade = 1
                    #Similaridade.objects.create(codigo_referencia=codigo_referencia, codigo_solucao=codigo_solucao, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)
                    #Similaridade.objects.create(codigo_referencia=codigo_solucao, codigo_solucao=codigo_referencia, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)

                    algoritmo = "TextEdit"
                    #print("TextEdit %s(%d) %s(%d)" %(codigo_referencia.arquivo, i, codigo_solucao.arquivo, j))
                    #coeficiente_similaridade = 1
                    #Similaridade.objects.create(codigo_referencia=codigo_referencia, codigo_solucao=codigo_solucao, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)
                    #Similaridade.objects.create(codigo_referencia=codigo_solucao, codigo_solucao=codigo_referencia, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)

                    algoritmo = "Tree"
                    #print("Tree %s(%d) %s(%d)" %(codigo_referencia.arquivo, i, codigo_solucao.arquivo, j))
                    #coeficiente_similaridade = 1
                    #Similaridade.objects.create(codigo_referencia=codigo_referencia, codigo_solucao=codigo_solucao, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)
                    #Similaridade.objects.create(codigo_referencia=codigo_solucao, codigo_solucao=codigo_referencia, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)
                else :
                    algoritmo = "Jaccard"
                    #print("Jaccard %s(%d) %s(%d)" %(codigo_referencia.arquivo, i, codigo_solucao.arquivo, j))
                    #coeficiente_similaridade = tag._token(source1, source2)
                    #Similaridade.objects.create(codigo_referencia=codigo_referencia, codigo_solucao=codigo_solucao, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)
                    #Similaridade.objects.create(codigo_referencia=codigo_solucao, codigo_solucao=codigo_referencia, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)

                    algoritmo = "TextEdit"
                    #print("TextEdit %s(%d) %s(%d)" %(codigo_referencia.arquivo, i, codigo_solucao.arquivo, j))
                    #coeficiente_similaridade = edit._text(source1, source2)
                    #Similaridade.objects.create(codigo_referencia=codigo_referencia, codigo_solucao=codigo_solucao, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)
                    #Similaridade.objects.create(codigo_referencia=codigo_solucao, codigo_solucao=codigo_referencia, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)

                    algoritmo = "Tree"
                    #print("Tree %s(%d) %s(%d)" %(codigo_referencia.arquivo, i, codigo_solucao.arquivo, j))
                    #coeficiente_similaridade = tree._main(source1, source2)
                    #Similaridade.objects.create(codigo_referencia=codigo_referencia, codigo_solucao=codigo_solucao, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)
                    #Similaridade.objects.create(codigo_referencia=codigo_solucao, codigo_solucao=codigo_referencia, algoritmo=algoritmo, coeficiente_similaridade=coeficiente_similaridade)
    except Exception as e:
        print("Similaridades Error " + str(e))

    similaridades = Similaridade.objects.filter(codigo_referencia__problema=problema).order_by('algoritmo')

    data = {}
    data['problema'] = problema
    data['similaridades_list'] = similaridades
    data['submissoes_list'] = submissoes
    data['problemas_list'] = problemas
    data['problemas_publicados_list'] = problemas_publicados
    data['count_problemas'] = problemas_count
    data['count_submissoes'] = submissoes_count
    data['count_avaliacoes_realizadas'] = avaliacoes_realizadas_count
    data['count_avaliacoes_pendentes'] = (count_avaliacoes_pendentes - avaliacoes_realizadas_count)
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_agrupamentos(request, pk, template_name='programacao/admin_agrupamentos.html'):
    problema = get_object_or_404(Problema, pk=pk)
    codigo_referencia = Codigo.objects.get(problema=problema, referencia=True)
    codigo_list = Codigo.objects.filter(problema=problema, referencia=False, medidas_ok=True)

    medida_corretude_funcional = 0
    medida_complexity = 1
    sim_jaccard = 2
    sim_text_edit = 3
    sim_tree_edit = 4
    medida_distinct_operators = 5
    medida_distinct_operands = 6
    medida_loc = 7
    medida_total_number_operators = 8
    medida_total_number_operands = 9
    medida_vocabulary = 10
    medida_length = 11

    n = 7 # quantidade de medidas
    str_medidas = [] # armazena as strings de ativacao
    for x in range(1, 2**n):
        str_medidas.append(''.join(str((x>>i)&1) for i in xrange(n-1,-1,-1)))

#    normalizacao = [0, 1] #0- sem normalizacao, 1-normalizado em relacao a solucao de referencia
    norm = ['não', '']
    normalizacao = 0

    list_all = []
    codigos_id = []
    medidas_valores = []
    medidas_nomes = []
    # iteracoes
    for iteracao in str_medidas:
        print(iteracao)
        list_iteracao = []
        codigos_id = []
        codigos_medidas = []
        medidas_nomes = []
        for codigo in codigo_list:
            codigos_id.append(codigo.id)
            bits_ativacao = iteracao[::-1]
            medidas_valores = []
            medidas_nomes = []
            # apenas solucoes corretas sintaticamente serao consideradas       
            if (bits_ativacao[medida_corretude_funcional] == '1') :
                medidas_valores.append(codigo.get_corretude_funcional())
                medidas_nomes.append('corretude_funcional,')
            if (bits_ativacao[medida_complexity] == '1') :
                medidas_valores.append(codigo.get_complexity(codigo_referencia, normalizado=normalizacao))    
                medidas_nomes.append('complexity,')
            if (bits_ativacao[sim_jaccard] == '1') :
                medidas_valores.append(codigo.get_similarity_jaccard(codigo_referencia))
                medidas_nomes.append('jaccard,')
            if (bits_ativacao[sim_text_edit] == '1') :
                medidas_valores.append(codigo.get_similarity_text_edit_distance(codigo_referencia))
                medidas_nomes.append('text_edit,')    
            if (bits_ativacao[sim_tree_edit] == '1') :
                medidas_valores.append(codigo.get_similarity_tree_edit_distance(codigo_referencia))
                medidas_nomes.append('tree_edit,')
            if (bits_ativacao[medida_distinct_operators] == '1') :
                value = codigo.get_distinct_operators(codigo_referencia, normalizado=normalizacao)
                if value == None:
                    value = 0
                medidas_valores.append(value)
                medidas_nomes.append('distinct_operators,')
            if (bits_ativacao[medida_distinct_operands] == '1') :
                value = codigo.get_distinct_operands(codigo_referencia, normalizado=normalizacao)
                if value == None:
                    value = 0
                medidas_valores.append(value)
                medidas_nomes.append('distinct_operands')

            codigos_medidas.append(medidas_valores)

        list_iteracao = [medidas_nomes, codigos_id, codigos_medidas]
        list_all.append(list_iteracao)

    # agrupamento
    ks = [10]
    for k in ks:
        for e in list_all:
            medidas=''.join(e[0])
            algoritmo = 'kmeans k=%d %s normalizado' % (k, norm[normalizacao])
            print('kmeans k=%d %s normalizado - %s' % (k, norm[normalizacao], medidas) )
            agrupamento = Agrupamento.objects.create(algoritmo=algoritmo, medidas=medidas)

            ids = list(e[1])
            inputs = list(e[2])
            kmeans_ids = np.array(ids) # codigos_ids
            kmeans_input = np.array(inputs) # codigos_medidas

            centroids,_= kmeans(kmeans_input, k)
            idx,_ = vq(kmeans_input, centroids)

            grupos = list(idx)
            for i in range(len(ids)):
                codigo = Codigo.objects.get(id=ids[i])
                grupo = grupos[i]
                AvaliacaoAgrupamento.objects.create(codigo=codigo, agrupamento=agrupamento, grupo=grupo)

    avaliacoes_agrupamento_list = AvaliacaoAgrupamento.objects.filter(codigo__problema=problema).order_by('agrupamento__algoritmo', 'agrupamento__medidas', 'grupo')

    data = {}
    data['problema'] = problema
    data['avaliacoes_agrupamento_list'] = avaliacoes_agrupamento_list
    ###########################################################################################
    ###########################################################################################
    codigo_referencia = Codigo.objects.get(problema=problema, referencia=True)
    id_especialista = 10

    # gerar
    agrupamento_all = Agrupamento.objects.all()
    avaliacoes_agrupamento_list = []
    for agrupamento in agrupamento_all :
        # para todo agrupamento a solucao de referencia tem avaliacao maxima
        # TODO avaliacao maxima = criterio maximo (pode ser 10, pode ser A, ...)
        AvaliacaoAgrupamento.objects.create(codigo=codigo_referencia, agrupamento=agrupamento, avaliacao=10)

        print(agrupamento.medidas)
        agrupamento_grupos = agrupamento.grupos(problema)
        avaliacoes_grupo = []
        for grupo in agrupamento_grupos:
            avaliacoes_agrupamento = AvaliacaoAgrupamento.objects.filter(codigo__problema=problema, agrupamento=agrupamento, grupo=grupo)
            distancias = []
            for avaliacao in avaliacoes_agrupamento:
                distancia = avaliacao.codigo.distancia(codigo_referencia, agrupamento)
                distancias.append(distancia)
            distancia_min = min(distancias)
            distancia_max = max(distancias)
            codigo_referencia_grupo = None
            for avaliacao in avaliacoes_agrupamento:
                distancia = avaliacao.codigo.distancia(codigo_referencia, agrupamento)
                if (distancia == distancia_min) :
                    codigo_referencia_grupo = avaliacao.codigo

                    especialista = Especialista.objects.get(user_id=id_especialista)
                    avaliacao_especialista = AvaliacaoEspecialista.objects.get(codigo=codigo_referencia_grupo, especialista=especialista)

                    avaliacao.avaliacao = avaliacao_especialista.avaliacao
                    avaliacao.save()
            for avaliacao in avaliacoes_agrupamento:
                avaliacao_referencia_grupo = AvaliacaoAgrupamento.objects.get(codigo=codigo_referencia_grupo, agrupamento=agrupamento, grupo=grupo)
                 # todas as solucoes do grupo sao avaliadas da mesma forma
                avaliacao.avaliacao = avaliacao_referencia_grupo.avaliacao
                avaliacao.save()


    #apresentar
    codigo_list = Codigo.objects.filter(problema=problema)
    codigo_avaliacoes = []
    count = 0
    for codigo in codigo_list:
        print("codigo %d" % count)
        count+=1
        temp = []
        temp.append(codigo.arquivo)
        avaliacoes_agrupamento_list = AvaliacaoAgrupamento.objects.filter(codigo=codigo)
        avaliacoes_agrupamento_temp = []
        for avaliacao in avaliacoes_agrupamento_list:
            avaliacoes_agrupamento_temp.append(avaliacao.avaliacao)
        temp.append(avaliacoes_agrupamento_temp)

        e1 = Especialista.objects.get(id = 1)
        e2 = Especialista.objects.get(id = id_especialista)
        especialista_all = [e1,e2]

        avaliacoes_especialista_temp = []
        for especialista in especialista_all:
            try :
                avaliacao_especialista = AvaliacaoEspecialista.objects.get(codigo=codigo, especialista=especialista)
                avaliacoes_especialista_temp.append(avaliacao_especialista.avaliacao)
            except:
                pass
            temp.append(avaliacoes_especialista_temp)

        codigo_avaliacoes.append(temp)

    nome = "data-%d.csv" % problema.id
    print(nome)
    arquivo = open(nome, "w")
    arquivo.write("codigo, ")
    for agrupamento in avaliacoes_agrupamento_list :
        arquivo.write("A%d, " % agrupamento.agrupamento.id)
    for especialista in especialista_all :
        arquivo.write("E%d, " % especialista.id)
    arquivo.write("\n")

    for avaliacao in codigo_avaliacoes :
        arquivo.write("%s, " % avaliacao[0])
        for avaliacao_agrupamento in avaliacao[1] :
            if (avaliacao_agrupamento) :
                arquivo.write("%s, " % avaliacao_agrupamento)
            else :
                arquivo.write("0, ")
        for avaliacao_especialista in avaliacao[2] :
            if (avaliacao_especialista) :
                arquivo.write("%s, " % avaliacao_especialista)
            else :
                arquivo.write("0, ")
        arquivo.write("\n")
    arquivo.close()

    data['problema'] = problema
    data['codigo_avaliacoes'] = codigo_avaliacoes
    data['avaliacoes_agrupamento_list'] = avaliacoes_agrupamento_list
    data['especialista_all'] = especialista_all

    ###########################################################################################
    ###########################################################################################
    
    ###########################################################################################
    ###########################################################################################

    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_ver_agrupamentos(request, pk, template_name='programacao/admin_agrupamentos.html'):
    problema = get_object_or_404(Problema, pk=pk)
    avaliacoes_agrupamento_list = AvaliacaoAgrupamento.objects.filter(codigo__problema=problema).order_by('agrupamento__algoritmo', 'agrupamento__medidas', 'grupo')

    data = {}
    data['problema'] = problema
    data['avaliacoes_agrupamento_list'] = avaliacoes_agrupamento_list
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_autor')
def admin_notas(request, pk, template_name='programacao/admin_notas.html'):
    problema = get_object_or_404(Problema, pk=pk)
    
    codigo_referencia = Codigo.objects.get(problema=problema, referencia=True)
    id_especialista = 6

    # gerar
    agrupamento_all = Agrupamento.objects.all()
    avaliacoes_agrupamento_list = []
    for agrupamento in agrupamento_all :
        # para todo agrupamento a solucao de referencia tem avaliacao maxima
        # TODO avaliacao maxima = criterio maximo (pode ser 10, pode ser A, ...)
        AvaliacaoAgrupamento.objects.create(codigo=codigo_referencia, agrupamento=agrupamento, avaliacao=10)

        print(agrupamento.medidas)
        agrupamento_grupos = agrupamento.grupos(problema)
        avaliacoes_grupo = []
        for grupo in agrupamento_grupos:
            avaliacoes_agrupamento = AvaliacaoAgrupamento.objects.filter(codigo__problema=problema, agrupamento=agrupamento, grupo=grupo)
            distancias = []
            for avaliacao in avaliacoes_agrupamento:
                distancia = avaliacao.codigo.distancia(codigo_referencia, agrupamento)
                distancias.append(distancia)
            distancia_min = min(distancias)
            distancia_max = max(distancias)
            codigo_referencia_grupo = None
            for avaliacao in avaliacoes_agrupamento:
                distancia = avaliacao.codigo.distancia(codigo_referencia, agrupamento)
                if (distancia == distancia_min) :
                    codigo_referencia_grupo = avaliacao.codigo

                    especialista = Especialista.objects.get(user_id=id_especialista)
                    avaliacao_especialista = AvaliacaoEspecialista.objects.get(codigo=codigo_referencia_grupo, especialista=especialista)

                    avaliacao.avaliacao = avaliacao_especialista.avaliacao
                    avaliacao.save()
            for avaliacao in avaliacoes_agrupamento:
                avaliacao_referencia_grupo = AvaliacaoAgrupamento.objects.get(codigo=codigo_referencia_grupo, agrupamento=agrupamento, grupo=grupo)
                 # todas as solucoes do grupo sao avaliadas da mesma forma
                avaliacao.avaliacao = avaliacao_referencia_grupo.avaliacao
                avaliacao.save()


    #apresentar
    codigo_list = Codigo.objects.filter(problema=problema)
    codigo_avaliacoes = []
    count = 0
    for codigo in codigo_list:
        print("codigo %d" % count)
        count+=1
        temp = []
        temp.append(codigo.arquivo)
        avaliacoes_agrupamento_list = AvaliacaoAgrupamento.objects.filter(codigo=codigo)
        avaliacoes_agrupamento_temp = []
        for avaliacao in avaliacoes_agrupamento_list:
            avaliacoes_agrupamento_temp.append(avaliacao.avaliacao)
        temp.append(avaliacoes_agrupamento_temp)

        e1 = Especialista.objects.get(id = 1)
        e2 = Especialista.objects.get(id = id_especialista)
        especialista_all = [e1,e2]

        avaliacoes_especialista_temp = []
        for especialista in especialista_all:
            try :
                avaliacao_especialista = AvaliacaoEspecialista.objects.get(codigo=codigo, especialista=especialista)
                avaliacoes_especialista_temp.append(avaliacao_especialista.avaliacao)
            except:
                pass
            temp.append(avaliacoes_especialista_temp)

        codigo_avaliacoes.append(temp)

    nome = "data-%d.csv" % problema.id
    print(nome)
    arquivo = open(nome, "w")
    arquivo.write("codigo, ")
    for agrupamento in avaliacoes_agrupamento_list :
        arquivo.write("A%d, " % agrupamento.agrupamento.id)
    for especialista in especialista_all :
        arquivo.write("E%d, " % especialista.id)
    arquivo.write("\n")

    for avaliacao in codigo_avaliacoes :
        arquivo.write("%s, " % avaliacao[0])
        for avaliacao_agrupamento in avaliacao[1] :
            if (avaliacao_agrupamento) :
                arquivo.write("%s, " % avaliacao_agrupamento)
            else :
                arquivo.write("0, ")
        for avaliacao_especialista in avaliacao[2] :
            if (avaliacao_especialista) :
                arquivo.write("%s, " % avaliacao_especialista)
            else :
                arquivo.write("0, ")
        arquivo.write("\n")
    arquivo.close()

    data = {}
    data['problema'] = problema
    data['codigo_avaliacoes'] = codigo_avaliacoes
    data['avaliacoes_agrupamento_list'] = avaliacoes_agrupamento_list
    data['especialista_all'] = especialista_all
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_especialista')
def especialista_index(request, template_name='programacao/especialista_index.html'):
    problemas = Problema.objects.filter(publicar=True)
    problemas_count = Problema.objects.filter(publicar=True).count()

    submissoes_count = Codigo.objects.filter(problema__publicar=True).count()

    user = request.user
    especialista = Especialista.objects.get(user_id=user.id)
    avaliacoes_realizadas_count = AvaliacaoEspecialista.objects.filter(especialista=especialista).count()

    problemas_dict = {}
    count_avaliacoes_pendentes = 0
    for problema in problemas:
        count_avaliacoes = problema.get_avaliacoes().filter(especialista=especialista).count()
        problemas_dict[problema.id] = count_avaliacoes
        count_avaliacoes_pendentes = count_avaliacoes_pendentes + problema.get_count_avaliacoes_pendentes()

    data = {}
    data['problemas_list'] = problemas
    data['count_problemas'] = problemas_count
    data['count_submissoes'] = submissoes_count
    data['count_avaliacoes_realizadas'] = avaliacoes_realizadas_count
    data['count_avaliacoes_pendentes'] = (count_avaliacoes_pendentes - avaliacoes_realizadas_count)
    data['problemas_dict'] = problemas_dict
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_especialista')
def especialista_edit(request, template_name='programacao/especialista_edit.html'):
    user = request.user
    especialista = Especialista.objects.get(user_id=user.id)

    user_form = UserEditForm(request.POST or None, instance=user)
    especialista_form = EspecialistaForm(request.POST or None, instance=especialista)

    if especialista_form.is_valid() and user_form.is_valid():
        user_form.save()
        especialista_form.save()
        return redirect('programacao:especialista_edit')
    
    data = {}
    data['user_form'] = user_form
    data['especialista_form'] = especialista_form
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_especialista')
def especialista_visualizar_problema(request, pk, template_name='programacao/especialista_visualizar_problema.html'):
    problema = get_object_or_404(Problema, pk=pk)

    codigos_problema = Codigo.objects.filter(problema=problema)

    user = request.user
    especialista = Especialista.objects.get(user_id=user.id)
    avaliacao_list = AvaliacaoEspecialista.objects.filter(especialista=especialista, codigo__in=codigos_problema)

    codigos_exclude = []
    for avaliacao in avaliacao_list:
        c = Codigo.objects.get(id=avaliacao.codigo_id)
        codigos_exclude.append(c.id)
    codigos_list = Codigo.objects.filter(problema=problema, id_turma=problema.id_turma_principal).exclude(id__in=codigos_exclude)

    criterios = None
    try:
        criterios = CriterioEspecialista.objects.get(problema=problema, especialista=especialista)
    except:
        pass
    form = CriterioEspecialistaForm(request.POST or None, instance=criterios)
    if form.is_valid():
        criterio = form.save(commit=False)
        criterio.problema = problema
        criterio.especialista = especialista
        criterio.save()

    data = {}
    data['form'] = form
    data['problema'] = problema
    data['codigos_list'] = codigos_list
    data['avaliacao_list'] = avaliacao_list
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_especialista')#@permission_required('programacao.is_especialista')
def especialista_avaliar(request, pk, template_name='programacao/especialista_avaliar.html'):
    codigo = get_object_or_404(Codigo, pk=pk)
    form = AvaliacaoEspecialistaForm(request.POST or None)

    source = codigo.display_text()

    if request.method=='POST':
        if form.is_valid():
            avaliacao_especialista = form.save(commit=False)

            avaliacao_especialista.codigo = codigo

            user = request.user
            especialista = Especialista.objects.get(user_id=user.id)
            avaliacao_especialista.especialista = especialista

            avaliacao_especialista.save()
            return redirect('programacao:especialista_visualizar_problema', pk=codigo.problema_id)

    data = {}
    data['codigo'] = codigo
    data['source'] = source
    data['form'] = form
    return render(request, template_name, data)


@login_required
@permission_required('programacao.view_especialista')
def especialista_editar_avaliacao(request, pk, template_name='programacao/especialista_avaliar.html'):
#    user = request.user
#    especialista = Especialista.objects.get(user_id=user.id)
#    codigo = Codigo.objects.get(id=pk)
#    avaliacao = AvaliacaoEspecialista.objects.get(codigo=codigo, especialista=especialista)
    avaliacao = get_object_or_404(AvaliacaoEspecialista, pk=pk)
    form = AvaliacaoEspecialistaForm(request.POST or None, instance=avaliacao)

    source = avaliacao.codigo.display_text()

    if request.method=='POST':
        if form.is_valid():
            form.save()
            return redirect('programacao:especialista_visualizar_problema', pk=avaliacao.codigo.problema_id)

    data = {}
    data['avaliacao'] = avaliacao
    data['source'] = source
    data['form'] = form
    return render(request, template_name, data)


