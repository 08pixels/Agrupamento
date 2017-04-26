# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.models import ModelForm
from django.core.files import File

from programacao.validators import valida_avaliacao

class Problema(models.Model):
    nome=models.CharField(max_length=100)
    id_huxley=models.IntegerField(null=True, blank=True, default=None)
    id_turma_principal=models.IntegerField(null=True, blank=True, default=None)
    enunciado=models.TextField(max_length=1000, null=True, blank=True, default=None)
    entrada=models.TextField(max_length=1000, null=True, blank=True, default=None)
    saida=models.TextField(max_length=1000, null=True, blank=True, default=None)
    conteudo=models.TextField(max_length=1000, null=True, blank=True, default=None)
    publicar=models.BooleanField(default=False)

    def __unicode__(self):
        return self.nome

    def avaliacao_concluida(self):
        if self.get_count_avaliacoes_pendentes() == 0 :
            return True
        return False

    def get_count_avaliacoes_pendentes(self):
        return Codigo.objects.filter(problema_id=self.id, id_turma=self.id_turma_principal).count()

    def get_count_confirmacoes_pendentes(self):
        codigos_principais = Codigo.objects.filter(problema_id=self.id, id_turma=self.id_turma_principal)
        return Codigo.objects.exclude(codigos_principais).count()

    def get_avaliacoes(self):
        return AvaliacaoEspecialista.objects.filter(codigo__problema_id=self.id)

    #def get_confirmacoes(self):
    #    return Codigo.objects.filter(problema_id=self.id, id_turma!=self.id_turma_principal).count()


class Codigo(models.Model):
    arquivo=models.CharField(max_length=100)
    id_turma=models.IntegerField(null=True, blank=True, default=None)
    referencia=models.BooleanField(default=False)
    CHOICES_LINGUAGEM=(("1","C"),("2","C++"),("3","Python 2.x"),("4","Python 3.x"),("5","Java"),("6","Pascal"),("7","Outra"))
    linguagem=models.CharField(choices=CHOICES_LINGUAGEM,default=None,max_length=50,blank=True,null=True)
    problema=models.ForeignKey('Problema',default=None)
    medidas_ok=models.BooleanField(default=False)
    # medidas
    medida_corretude_sintatica=models.BooleanField(default=False)
    medida_corretude_funcional=models.FloatField(null=True, blank=True, default=None)
    medida_complexity=models.FloatField(null=True, blank=True, default=None)
    medida_loc=models.FloatField(null=True, blank=True, default=None)
    medida_lloc=models.FloatField(null=True, blank=True, default=None)
    medida_sloc=models.FloatField(null=True, blank=True, default=None)
    #medida_comments=models.FloatField(null=True, blank=True, default=None)
    #medida_multi=models.FloatField(null=True, blank=True, default=None)
    medida_blank=models.FloatField(null=True, blank=True, default=None)
    medida_single_comments=models.FloatField(null=True, blank=True, default=None)
    medida_distinct_operators=models.FloatField(null=True, blank=True, default=None)
    medida_distinct_operands=models.FloatField(null=True, blank=True, default=None)
    medida_total_number_operators=models.FloatField(null=True, blank=True, default=None)
    medida_total_number_operands=models.FloatField(null=True, blank=True, default=None)
    medida_vocabulary=models.FloatField(null=True, blank=True, default=None)
    medida_length=models.FloatField(null=True, blank=True, default=None)
    medida_calculated_length=models.FloatField(null=True, blank=True, default=None)
    medida_volume=models.FloatField(null=True, blank=True, default=None)
    medida_difficulty=models.FloatField(null=True, blank=True, default=None)
    medida_effort=models.FloatField(null=True, blank=True, default=None)
    medida_time=models.FloatField(null=True, blank=True, default=None)
    medida_bugs=models.FloatField(null=True, blank=True, default=None)
    medida_mi=models.FloatField(null=True, blank=True, default=None)

    def __unicode__(self):
        return self.arquivo

    def get_abs_path(self):
        return os.path.join(settings.MEDIA_URL, 'codigos', str(self.problema.id_huxley), str(self.id_turma), self.arquivo)

    def display_text(self):
        source_file = open(os.path.join(settings.MEDIA_ROOT, 'codigos', str(self.problema.id_huxley), str(self.id_turma), self.arquivo), 'r')
        return source_file.read()

    def get_corretude_funcional(self) :
        return self.medida_corretude_funcional

    def get_complexity(self, solucao_referencia, normalizado=0) :
        if (normalizado == 0) :
            return self.medida_complexity
        # normalizado em relacao ao valor da solucao de referencia
        elif (normalizado == 1) :
            return self.medida_complexity / solucao_referencia.medida_complexity

    def get_distinct_operators(self, solucao_referencia, normalizado=0) :
        if (normalizado == 0) :
            return self.medida_distinct_operators
        # normalizado em relacao ao valor da solucao de referencia
        elif (normalizado == 1) :
            return self.medida_distinct_operators / solucao_referencia.medida_distinct_operators

    def get_distinct_operands(self, solucao_referencia, normalizado=0) :
        if (normalizado == 0) :
            return self.medida_distinct_operands
        # normalizado em relacao ao valor da solucao de referencia
        elif (normalizado == 1) :
            return self.medida_distinct_operands / solucao_referencia.medida_distinct_operands

    def get_similarity_jaccard(self, solucao_referencia) :
        sim = Similaridade.objects.get(codigo_solucao_id=self.id, codigo_referencia_id = solucao_referencia.id, algoritmo = 'Jaccard')
        return sim.coeficiente_similaridade

    def get_similarity_text_edit_distance(self, solucao_referencia) :
        sim = Similaridade.objects.get(codigo_solucao_id=self.id, codigo_referencia_id = solucao_referencia.id, algoritmo = 'TextEdit')
        return sim.coeficiente_similaridade

    def get_similarity_tree_edit_distance(self, solucao_referencia) :
        sim = Similaridade.objects.get(codigo_solucao_id=self.id, codigo_referencia_id = solucao_referencia.id, algoritmo = 'Tree')
        return sim.coeficiente_similaridade

    def distancia(self, solucao_referencia, agrupamento) :
        medidas = agrupamento.medidas.split(',')
        distancia = 0
        for medida in medidas :
            if medida == 'corretude_funcional':
                distancia = distancia + (100 - self.get_corretude_funcional()) / 100
            if medida == 'complexity':
                distancia = distancia + 1 - self.get_complexity(solucao_referencia, 1)
            if medida == 'jaccard':
                distancia = distancia + self.get_similarity_jaccard(solucao_referencia)
            if medida == 'text_edit':
                distancia = distancia + self.get_similarity_text_edit_distance(solucao_referencia)
            if medida == 'tree_edit':
                distancia = distancia + self.get_similarity_tree_edit_distance(solucao_referencia)
            if medida == 'distinct_operators':
                distancia = distancia + 1 - self.get_distinct_operators(solucao_referencia, 1)
            if medida == 'distinct_operands':
                distancia = distancia + 1 - self.get_distinct_operands(solucao_referencia, 1)
        return distancia/len(medidas)


class Similaridade(models.Model):
    codigo_referencia = models.ForeignKey('Codigo', related_name='codigo_referencia', default=None)
    codigo_solucao = models.ForeignKey('Codigo', related_name='codigo_solucao', default=None)
    CHOICES_ALGORITMO=(("1","Jaccard"),("2","TextEdit"),("3","Tree"))
    algoritmo=models.CharField(choices=CHOICES_ALGORITMO,default=None,max_length=50,blank=True,null=True)
    coeficiente_similaridade = models.FloatField(null=True, blank=True, default=None)

    def __unicode__(self):
        return "algoritmo %s" % (self.algoritmo)


class Especialista(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    nome = models.CharField(max_length=200)
    experiencia_professor =models.BooleanField(default=False, verbose_name="Possui experiência como professor")
    CHOICES_NIVEL = (("1","Doutorado"),("2","Mestrado"),("3","Especialização"),("4","Graduação"))
    nivel_formacao = models.CharField(choices=CHOICES_NIVEL,default=None,max_length=50,blank=True,null=True, verbose_name="Nível de formação")
    experiencia_monitor = models.BooleanField(default=False, verbose_name="Possui experiência como monitor de disciplina")
    experiencia_monitor_programacao = models.BooleanField(default=False, verbose_name="Possui experiência como monitor de disciplina de programação")

    def __unicode__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('programacao:especialista_edit', kwargs={'pk': self.pk})
       
    class Meta:
        permissions=(('view_especialista', 'view_especialista'), ('view_autor', 'view_autor'))


class CriterioEspecialista(models.Model):
    problema = models.ForeignKey('Problema')
    especialista = models.ForeignKey('Especialista')
    criterios=models.TextField(max_length=1000, null=True, blank=True, default=None, verbose_name='Critérios adotados na correção')

    def __unicode__(self):
        return ("%s avaliou %s como %s" % (self.especialista, self.problema, self.criterios))

    def get_absolute_url(self):
        return reverse(viewname='programacao:especialista_avaliar', kwargs={'pk': self.pk})


class AvaliacaoEspecialista(models.Model):
    codigo = models.ForeignKey('Codigo')
    especialista = models.ForeignKey('Especialista')
    avaliacao = models.FloatField(null=True, blank=True, default=None, validators=[valida_avaliacao])
    feedback = models.TextField(max_length=1000, null=True, blank=True, default=None)
    observacao = models.TextField(max_length=1000, null=True, blank=True, default=None)

    def __unicode__(self):
        return ("%s avaliou %s como %.2f" % (self.especialista, self.codigo, self.avaliacao))

    def get_absolute_url(self):
        return reverse(viewname='programacao:especialista_avaliar', kwargs={'pk': self.pk})


class Agrupamento(models.Model):
    algoritmo = models.CharField(max_length=100, null=True, blank=True, default=None)
    descricao = models.CharField(max_length=100, null=True, blank=True, default=None)
    medidas = models.CharField(max_length=100, null=True, blank=True, default=None)

    def __unicode__(self):
        return "%s %s %s" % (self.algoritmo, self.descricao, self.medidas)

    def grupos(self, problema):
        from django.db import connection
        grupos = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT ag.grupo FROM safira_avaliar.programacao_avaliacaoagrupamento as ag, safira_avaliar.programacao_codigo as c WHERE c.id = ag.codigo_id AND c.problema_id = %d AND agrupamento_id = %d GROUP BY ag.grupo ORDER BY ag.grupo" % (problema.id, self.id))
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                else :
                    grupos.append(int(row[0]))
        return grupos


class AvaliacaoAgrupamento(models.Model):
    codigo = models.ForeignKey('Codigo')
    agrupamento = models.ForeignKey('Agrupamento')
    grupo = models.IntegerField(null=True, blank=True, default=None)

    avaliacao = models.FloatField(null=True, blank=True, default=None)
    feedback = models.TextField(max_length=1000, null=True, blank=True, default=None)

    def __unicode__(self):
        return ("%s avaliou %s" % (self.agrupamento, self.codigo))

    def get_absolute_url(self):
        return reverse(viewname='programacao:especialista_avaliar', kwargs={'pk': self.pk})

    def get_algoritmo(self):
        return self.agrupamento.algoritmo

    def get_medidas(self):
        return self.agrupamento.medidas


