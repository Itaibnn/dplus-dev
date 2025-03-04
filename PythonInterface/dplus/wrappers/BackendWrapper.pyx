# This file calls the backend using the PythonBackendWrapper
from PythonBackendWrapper cimport PythonBackendWrapper

cdef class BackendWrapper:
    cdef PythonBackendWrapper _wrapper

    def check_capabilities(self, tdrLevel):
        self._wrapper.CheckCapabilities(tdrLevel)

    def get_all_model_metadata(self):
        return self._wrapper.GetAllModelMetadata()

    def initialize_cache(self, cache_dir):
        self._wrapper.InitializeCache(cache_dir)

    def initialize_cache(self):
        self._wrapper.InitializeCache()

    def start_generate(self, state, useGPU):
        self._wrapper.StartGenerate(state, useGPU)

    def start_generate_2D(self, state, useGPU):
        self._wrapper.StartGenerate2D(state, useGPU)

    def get_job_status(self):
        return self._wrapper.GetJobStatus();

    def get_generate_results(self):
        return self._wrapper.GetGenerateResults();

    def get_generate_2D_results(self):
        return self._wrapper.GetGenerate2DResults();

    def save_amp(self, modelptr, path):
        self._wrapper.SaveAmplitude(modelptr, path.encode("utf-8"))

    def get_amp(self, modelptr):
        return self._wrapper.GetAmplitude(modelptr)

    def get_pdb(self, modelptr): 
        bytes_pdb = self._wrapper.GetPDB(modelptr)
        str_pdb = bytes_pdb.decode('utf-8')
        return str_pdb

    def get_model_ptrs(self):
        return list(self._wrapper.GetModelPtrs())

    def stop(self):
        self._wrapper.Stop()

