from qubricks import Measurement

class CustomMeasurement(Measurement):

	def init(self,**kwargs):
		'''
		Measurement.init should be specified by measurement subclasses.
		'''
		raise NotImplementedError("Measurement.init_measurement has not been implemented.")

	def measure(self,times,y_0s,params={},**kwargs):
		'''
		Measurement.measure is where the grunt work is done; and it should return 
		a numpy array of type Measurement.result_type, with shape
		Measurement.result_shape . Otherwise, anything is permitted in this method.
		'''
		raise NotImplementedError("Measurement.measure has not been implemented.")
	
	def result_type(self,*args,**kwargs):
		'''
		Measurement.result_type should return an object suitable for use as the dtype 
		argument in numpy. Otherwise, no restrictions; other than that it must also 
		agree with the datatype returned by Measurement.measure.
		'''
		raise NotImplementedError("Measurement.result_type has not been implemented.")

	def result_shape(self,*args,**kwargs):
		'''
		Measurement.result_shape should agree with the shape of the numpy array returned
		by Measurement.measure, but otherwise has no restrictions.
		'''
		raise NotImplementedError("Measurement.result_shape has not been implemented.")
