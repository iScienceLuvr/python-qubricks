from qubricks import Measurement

class CustomMeasurement(Measurement):
	'''
	Refer to the API documentation `Measurement` for more details.
	'''

	def init(self, *args, **kwargs):
		'''
		This method should initialise the Measurement instance in whatever way
		is necessary to prepare the instance for use. Note that any arguments 
		passed to the Measurement constructor will also be passed to this method.
		There is no restriction on the method signature for the init method.
		'''
		raise NotImplementedError("Measurement.init has not been implemented.")

	def measure(self, data=None, times=None, initial=None, params={}, **kwargs):
		'''
		This method should return the value of a measurement as a numpy array with
		data type and shape as specified in `result_type` and `result_shape` respectively.
		
		.. note:: It is possible to return types other than numpy array and still
			be compatible with iteration (see MeasurementWrapper) provided you overload
			the `iterate_results_init` and `iterate_results_add` methods.
			
		Implementations of `measure` will typically be provided by integration data
		by a `MeasurementWrapper` instance (which will be a structured numpy array 
		as returned by `Integrator.integrate) as the value for the `data` keyword.
		A consistent set of values for `times` and `initial` will also be passed.
		
		.. note:: If an implementation of `measure` omits the `data` keyword, QuBricks
			assumes that all integration required by the `measure` operator will be
			performed internally. It can use the reference to a QuantumSystem 
			instance at `Measurement.system` for this purpose. If the `data` keyword
			is present (for testing/etc), but pre-computed integration data is undesired,
			override the `is_independent` method to return `True`. If external data
			is *required*, then simply remove the default value of `data`.
		
		Apart from the required keywords: `data`, `times`, `initial` and `params`; any additional
		keywords can be specified. Refer to the documentation of `MeasurementWrapper` to 
		see how their values will filter through.
		
		.. note:: Although the keywords `times` and `initial` are necessary, it is not 
			necessary to use these keywords. As such, Measurement operators need not
			require an integration of the physical system.
		
		:param data: Data from a QuantumSystem.integrate call, or None.
		:type data: numpy.ndarray or None
		:param times: Sequence of times of interest.
		:type times: iterable
		:param initial: The initial state vectors/ensembles with which to start integrating.
		:type initial: str or iterable
		:param params: Parameter context to use during this measurement. Parameter types can be anything supported by Parameters.
		:type params: dict
		:param kwargs: Any other keyword arguments not collected explicitly.
		:type kwargs: dict
		'''
		raise NotImplementedError("Measurement.measure has not been implemented.")
	
		
	def result_type(self, *args, **kwargs):
		'''
		This method should return an object suitable for use as the dtype
		argument in a numpy array constructor. Otherwise, no restrictions; other than that it must also
		agree with the data-type returned by `Measurement.measure`.
		
		This method will receive all arguments and keyword arguments passed to
		`iterate_results_init`, where it is used to initialise the storage of 
		measurement results.
		'''
		raise NotImplementedError("Measurement.result_type has not been implemented.")
	
	def result_shape(self, *args, **kwargs):
		'''
		This method should return a tuple describing the shape of the numpy array to be returned
		by Measurement.measure.
		
		This method will receive all arguments and keyword arguments passed to
		`iterate_results_init`, where it is used to initialise the storage of 
		measurement results.
		'''
		raise NotImplementedError("Measurement.result_shape has not been implemented.")
	
#	The following is only needed if you do not want to receive pre-computed integration data.
# 	@property
# 	def is_independent(self):
# 		'''
# 		`True` if this Measurement instance does all required integration internally (and so should
# 		not receive pre-computed integration data). `False` otherwise. The default implementation is 
# 		`False`.
# 		'''
# 		return False
