#include "embeddedr.h"

/* Helper variable to store R's status
 */
const unsigned int const RPY_R_INITIALIZED = 0x01;
const unsigned int const RPY_R_BUSY = 0x02;
/* Initial status is 0 */
static unsigned int embeddedR_status = 0;

/* R's precious list-like*/
//static SEXP RPY_R_Precious = NULL;
static PyObject *Rpy_R_Precious;

static inline void embeddedR_setlock(void) {
  embeddedR_status = embeddedR_status | RPY_R_BUSY;
}
static inline void embeddedR_freelock(void) {
  embeddedR_status = embeddedR_status ^ RPY_R_BUSY;
}
static inline unsigned int rpy_has_status(unsigned int status) {
  return (embeddedR_status & status) == status;
}

static void SexpObject_clear(SexpObject *sexpobj)
{
  if (sexpobj->count <= 0) {
    printf("Warning: clearing an R object with a refcount <= zero.\n");
  }

  sexpobj->count--;

#ifdef RPY_VERBOSE
  printf("R:%p -- sexp count is %i...", 
         sexpobj->sexp, sexpobj->count);
#endif
  if (((*sexpobj).count == 0) && (*sexpobj).sexp) {
#ifdef RPY_VERBOSE
    printf("freeing SEXP resources...");
#endif 

/*     if (sexpobj->sexp != R_NilValue) { */
/* #ifdef RPY_DEBUG_PRESERVE */
/*       printf("  PRESERVE -- Sexp_clear: R_ReleaseObject -- %p ",  */
/*              sexpobj->sexp); */
/*       preserved_robjects -= 1; */
/*       printf("-- %i\n", preserved_robjects); */
/* #endif  */
/*       int preserve_status = Rpy_ReleaseObject(sexpobj->sexp); */
/*       if (preserve_status == -1) { */
/* 	PyErr_Print(); */
/* 	PyErr_Clear(); */
/*       } */
/*     } */
    if (sexpobj->sexp != R_NilValue) {
      PyMem_Free(sexpobj);
    }
    /* self->ob_type->tp_free((PyObject*)self); */
#ifdef RPY_VERBOSE
    printf("done.\n");
#endif 
  }  
}

static void SexpObject_CObject_destroy(PyObject *rpycapsule)
{
  SexpObject *sexpobj_ptr = (SexpObject *)(PyCapsule_GetPointer(rpycapsule,
								"rpy2.rinterface._C_API_"));
  SexpObject_clear(sexpobj_ptr);
}

/* Keep track of R objects preserved by rpy2 
   Return NULL on failure (a Python exception being set) 
 */
static SexpObject* _Rpy_PreserveObject(SEXP object) {
  /* PyDict can be confused if an error has been raised.
     We put aside the exception if the case, to restore it at the end.
     FIXME: this situation can occur because of presumed shortcomings
     in the overall design of rpy2.
   */
  int reset_error_state = 0; 
  PyObject *ptype, *pvalue, *ptraceback;

  if (PyErr_Occurred()) {
    reset_error_state = 1;
    PyErr_Fetch(&ptype, &pvalue, &ptraceback);
  }

  PyObject *key = PyLong_FromVoidPtr((void *)object);
  PyObject *capsule = PyDict_GetItem(Rpy_R_Precious, key);
  SexpObject *sexpobj_ptr;
  /* capsule is a borrowed reference */
  if (capsule == NULL) {
    /* The R object is not yet tracked by rpy2 so we:
       - create a new SexpObject. 
       - create a capsule for it
       - put the capsule in the tracking dictionary
    */
    sexpobj_ptr = (SexpObject *)PyMem_Malloc(1 * sizeof(SexpObject));
    if (! sexpobj_ptr) {
      PyErr_NoMemory();
      return NULL;
    }
    sexpobj_ptr->count = 1;
    sexpobj_ptr->sexp = object;
    capsule = PyCapsule_New((void *)(sexpobj_ptr),
			    "rpy2.rinterface._C_API_",
			    SexpObject_CObject_destroy);
    if (PyDict_SetItem(Rpy_R_Precious, key, capsule) == -1) {
      Py_DECREF(key);
      Py_DECREF(capsule);
      return NULL;
    }
    Py_DECREF(capsule);
  } else {
    /* Reminder: capsule is a borrowed reference */
    sexpobj_ptr = (SexpObject *)(PyCapsule_GetPointer(capsule,
						      "rpy2.rinterface._C_API_"));
    if (sexpobj_ptr != NULL) {
      sexpobj_ptr->count++;
    }
  }
  Py_DECREF(key);
  
  if (reset_error_state) {
    if (PyErr_Occurred()) {
      PyErr_Print();
      PyErr_Clear();
    }
    PyErr_Restore(ptype, pvalue, ptraceback);
  }
  return sexpobj_ptr;
} 

static SexpObject* Rpy_PreserveObject(SEXP object) {
  SexpObject *res = _Rpy_PreserveObject(object);
  if (res == NULL) {
    printf("Error while logging preserved object (exception propagated up).\n");
  } else if (object != R_NilValue) {
    R_PreserveObject(object);
  }
  return res;
}
/* static int Rpy_PreserveObject(SEXP object) { */
/* R_ReleaseObject(RPY_R_Precious); */
/* PROTECT(RPY_R_Precious); */
/* RPY_R_Precious = CONS(object, RPY_R_Precious); */
/* UNPROTECT(1); */
/* R_PreserveObject(RPY_R_Precious); */
/* } */

static int Rpy_ReleaseObject(SEXP object) {
  /* PyDict can be confused if an error has been raised.
     We put aside the exception if the case, to restore it at the end.
     FIXME: this situation can occur because of presumed shortcomings
     in the overall design of rpy2.
   */
  int reset_error_state = 0; 
  PyObject *ptype, *pvalue, *ptraceback; 
  if (PyErr_Occurred()) {
    reset_error_state = 1;
    PyErr_Fetch(&ptype, &pvalue, &ptraceback);
  }

  PyObject *key = PyLong_FromVoidPtr((void *)object);
  PyObject *capsule = PyDict_GetItem(Rpy_R_Precious, key);
  /* capsule is a borrowed reference */
  if (capsule == NULL) {
    if (reset_error_state) {
      PyErr_Restore(ptype, pvalue, ptraceback);
      printf("Error:Trying to release object ID %ld while not preserved\n",
	     PyLong_AsLong(key));
    } else {
      PyErr_Format(PyExc_KeyError, 
		   "Trying to release object ID %ld while not preserved\n",
		   PyLong_AsLong(key));
    }
    Py_DECREF(key);
    return -1;
  } 

  SexpObject *sexpobj_ptr = (SexpObject *)(PyCapsule_GetPointer(capsule,
								"rpy2.rinterface._C_API_"));
  if (sexpobj_ptr == NULL) {
    if (reset_error_state) {
      if (PyErr_Occurred()) {
	PyErr_Print();
      }
      PyErr_Restore(ptype, pvalue, ptraceback);
    }
    Py_DECREF(key);
    return -1;
  }
  int res = 0;

  switch (sexpobj_ptr->count) {
  case 0:
    if (object == R_NilValue) {
      break;
    } else {
      res = -1;
      PyErr_Format(PyExc_ValueError,
		   "Preserved object ID %ld with a count of zero\n", 
		   PyLong_AsLong(key));
      Py_DECREF(key);
      return res;
      break;
    }
  case 1:
    /* By deleting the capsule from the dictionary, the count of the SexpObject
      will go down by one, reach zero, and the release of the R object 
      will be performed. */
    if (object == R_NilValue) {
      sexpobj_ptr->count--;
      break;
    } else {
      res = PyDict_DelItem(Rpy_R_Precious, key);
      if (res == -1)
	PyErr_Format(PyExc_ValueError,
		     "Occured while deleting preserved object ID %ld\n",  
		     PyLong_AsLong(key));
      break;
    }
  default:
    sexpobj_ptr->count--;
    break;
  }
  
  Py_DECREF(key);
  if (reset_error_state) {
    if (PyErr_Occurred()) {
      PyErr_Print();
    }
    PyErr_Restore(ptype, pvalue, ptraceback);
  }
  return res;
}
  /* SEXP parentnode, node; */
  /* Py_ssize_t res = -1; */
  /* if (isNull(RPY_R_Precious)) { */
  /*   return res; */
  /* } */
  /* res++; */
  /* if (object == CAR(RPY_R_Precious)) { */
  /*   RPY_R_Precious = CDR(RPY_R_Precious); */
  /*   return res; */
  /* } */
  /* parentnode = RPY_R_Precious; */
  /* node = CDR(RPY_R_Precious); */
  /* while (!isNull(node)) { */
  /*   res++; */
  /*   if (object == CAR(node)) { */
  /*     SETCDR(parentnode, CDR(node)); */
  /*     return res; */
  /*   } */
  /*   parentnode = node; */
  /*   node = CDR(node); */
  /* } */

PyDoc_STRVAR(Rpy_ProtectedIDs_doc,
             "Return a tuple with the R IDs for the objects protected\
 from R's garbage collection by rpy2, along with the number of rpy2 objects\
 protecting them from collection.\n");
/* Return a tuple with IDs of R objects protected by rpy2 and counts */
static PyObject* Rpy_ProtectedIDs(PyObject *self) {
  PyObject *key, *capsule;
  Py_ssize_t pos = 0;
  PyObject *ids = PyTuple_New(PyDict_Size(Rpy_R_Precious));
  Py_ssize_t pos_ids = 0;
  PyObject *id_count;
  SexpObject *sexpobject_ptr;

  while (PyDict_Next(Rpy_R_Precious, &pos, &key, &capsule)) {
    id_count = PyTuple_New(2);
    Py_INCREF(key);
    PyTuple_SET_ITEM(id_count, 0, key);
    sexpobject_ptr = (SexpObject *)(PyCapsule_GetPointer(capsule,
							 "rpy2.rinterface._C_API_"));
    PyTuple_SET_ITEM(id_count, 1, PyLong_FromLong(sexpobject_ptr->count));
    PyTuple_SET_ITEM(ids, pos_ids, id_count);
    pos_ids++;
  }
  return ids;  
}

/* return 0 on success, -1 on failure (and set an exception) */
static inline int Rpy_ReplaceSexp(PySexpObject *pso, SEXP rObj) {
  SexpObject *sexpobj_ptr = Rpy_PreserveObject(rObj);
  if (sexpobj_ptr == NULL) {
    return -1;
  }
  int res = Rpy_ReleaseObject(pso->sObj->sexp);
  pso->sObj = sexpobj_ptr;
  return res;
}
