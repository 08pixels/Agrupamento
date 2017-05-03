
class Codigo:

	def __init__(self, problema_id, arquivo, medida_corretude_funcional, medida_complexity, medida_distinct_operands, medida_distinct_operators):

		self.problema_id				= problema_id
		self.arquivo					= arquivo

		self.medida_corretude_funcional	= medida_corretude_funcional
		self.medida_complexity			= medida_complexity
		self.medida_distinct_operators	= medida_distinct_operators
		self.medida_distinct_operands	= medida_distinct_operands
		self.propriedades				= []
		self.grupo_id					= [None]