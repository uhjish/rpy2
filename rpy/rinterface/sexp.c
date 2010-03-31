#include <Python.h>

#include "r_utils.h"
#include "embeddedr.h"
#include "sexp.h"

void SexpObject_clear(SexpObject *sexpobj)
{

  (*sexpobj).count--;

#ifdef RPY_VERBOSE
  printf("R:%p -- sexp count is %i...", 
         sexpobj->sexp, sexpobj->count);
#endif
  if (((*sexpobj).count == 0) && (*sexpobj).sexp) {
#ifdef RPY_VERBOSE
    printf("freeing SEXP resources...");
#endif 

    if (sexpobj->sexp != R_NilValue) {
#ifdef RPY_DEBUG_PRESERVE
      printf("  PRESERVE -- Sexp_clear: R_ReleaseObject -- %p ", 
             sexpobj->sexp);
      preserved_robjects -= 1;
      printf("-- %i\n", preserved_robjects);
#endif 
    R_ReleaseObject(sexpobj->sexp);
    }
    PyMem_Free(sexpobj);
    /* self->ob_type->tp_free((PyObject*)self); */
#ifdef RPY_VERBOSE
    printf("done.\n");
#endif 
  }  
}

static void
Sexp_clear(PySexpObject *self)
{
  
  SexpObject_clear(self->sObj);

}


static void
Sexp_dealloc(PySexpObject *self)
{
  Sexp_clear(self);
  self->ob_type->tp_free((PyObject*)self);

  /* PyObject_Del(self); */
}


static PyObject*
Sexp_repr(PyObject *self)
{
  /* FIXME: make sure this is making any sense */
  SEXP sexp = RPY_SEXP((PySexpObject *)self);
  /* if (! sexp) {
   *  PyErr_Format(PyExc_ValueError, "NULL SEXP.");
   *  return NULL;
   *}
   */
  return PyString_FromFormat("<%s - Python:\%p / R:\%p>",
                             self->ob_type->tp_name,
                             self,
                             sexp);
}


static PyObject*
Sexp_typeof_get(PyObject *self)
{
  PySexpObject *pso = (PySexpObject*)self;
  SEXP sexp = RPY_SEXP(pso);
  if (! sexp) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }
  return PyInt_FromLong((long)TYPEOF(sexp));
}
PyDoc_STRVAR(Sexp_typeof_doc,
             "R internal SEXPREC type.");


static PyObject*
Sexp_do_slot(PyObject *self, PyObject *name)
{
  SEXP sexp = RPY_SEXP(((PySexpObject*)self));
  if (! sexp) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }
  if (! PyString_Check(name)) {
    PyErr_SetString(PyExc_TypeError, "The name must be a string.");
    return NULL;
  }
  char *name_str = PyString_AS_STRING(name);

  if (! R_has_slot(sexp, install(name_str))) {
    PyErr_SetString(PyExc_LookupError, "The object has no such attribute.");
    return NULL;
  }
  SEXP res_R = GET_SLOT(sexp, install(name_str));

  PyObject *res = (PyObject *)newPySexpObject(res_R);
  return res;
}
PyDoc_STRVAR(Sexp_do_slot_doc,
             "Returns the attribute/slot for an R object.\n"
             " The name of the slot (a string) is the only parameter for\n"
             "the method.\n"
             ":param name: string\n"
             ":rtype: instance of type or subtype :class:`rpy2.rinterface.Sexp`");

static PyObject*
Sexp_do_slot_assign(PyObject *self, PyObject *args)
{

  SEXP sexp = RPY_SEXP(((PySexpObject*)self));
  if (! sexp) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }

  char *name_str;
  PyObject *value;
  if (! PyArg_ParseTuple(args, "sO", 
                         &name_str,
                         &value)) {
    return NULL;
  }

  if (! PyObject_IsInstance(value, 
                          (PyObject*)&Sexp_Type)) {
      PyErr_Format(PyExc_ValueError, "Value must be an instance of Sexp.");
      return NULL;
  }

  SEXP value_sexp = RPY_SEXP((PySexpObject *)value);
  if (! value_sexp) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }

  SET_SLOT(sexp, install(name_str), value_sexp);
  Py_INCREF(Py_None);
  return Py_None;
}
PyDoc_STRVAR(Sexp_do_slot_assign_doc,
             "Set the attribute/slot for an R object.\n"
             "\n"
             ":param name: string\n"
             ":param value: instance of :class:`rpy2.rinterface.Sexp`");

static PyObject*
Sexp_named_get(PyObject *self)
{
  SEXP sexp = RPY_SEXP(((PySexpObject*)self));
  if (! sexp) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }
  unsigned int res = NAMED(sexp);
  return PyInt_FromLong((long)res);
}
PyDoc_STRVAR(Sexp_named_doc,
"Integer code for the R object reference-pseudo counting.\n\
This method corresponds to the macro NAMED.\n\
See the R-extensions manual for further details.");

void SexpObject_CObject_destroy(void *cobj)
{
  SexpObject* sexpobj_ptr = (SexpObject *)cobj;
  SexpObject_clear(sexpobj_ptr);
}

static PyObject*
Sexp_sexp_get(PyObject *self, void *closure)
{
  PySexpObject* rpyobj = (PySexpObject*)self;

  if (! RPY_SEXP(rpyobj)) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }
  
  RPY_INCREF(rpyobj);
  PyObject *res = PyCObject_FromVoidPtr(rpyobj->sObj, 
                                        SexpObject_CObject_destroy);
  return res;
}

static int
Sexp_sexp_set(PyObject *self, PyObject *obj, void *closure)
{
  if (! PyCObject_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "The value must be a CObject.");
    return -1;
  }

  SexpObject *sexpobj_orig = ((PySexpObject*)self)->sObj;
  SexpObject *sexpobj = (SexpObject *)(PyCObject_AsVoidPtr(obj));
  #ifdef RPY_DEBUG_COBJECT
  printf("Setting %p (count: %i) to %p (count: %i)\n", 
         sexpobj_orig, (int)sexpobj_orig->count,
         sexpobj, (int)sexpobj->count);
  #endif

  if ( (sexpobj_orig->sexp != R_NilValue) &
       (TYPEOF(sexpobj_orig->sexp) != TYPEOF(sexpobj->sexp))
      ) {
    PyErr_Format(PyExc_ValueError, 
                 "Mismatch in SEXP type (as returned by typeof)");
    return -1;
  }

  SEXP sexp = sexpobj->sexp;
  if (! sexp) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return -1;
  }

  /*FIXME: increment count seems needed, but is this leak free ? */
  sexpobj->count += 2;
  sexpobj_orig->count += 1;

  SexpObject_clear(sexpobj_orig);
  RPY_SEXP(((PySexpObject*)self)) = sexp;

  return 0;
}
PyDoc_STRVAR(Sexp_sexp_doc,
             "Opaque C pointer to the underlying R object");

static PyObject*
Sexp_refcount_get(PyObject *self)
{
  PySexpObject* rpyobj = (PySexpObject*)self;

  if (! RPY_SEXP(rpyobj)) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }
  
  PyObject *res = PyInt_FromLong((long)(rpyobj->sObj->count));
  return res;
}
PyDoc_STRVAR(Sexp_refcount_doc,
             "Reference counter for the underlying R object");


static PyObject*
Sexp_rsame(PyObject *self, PyObject *other)
{
  
  if (! PyObject_IsInstance(other, 
                            (PyObject*)&Sexp_Type)) {
    PyErr_Format(PyExc_ValueError, 
                 "Can only compare Sexp objects.");
    return NULL;
  }
  
  SEXP sexp_self = RPY_SEXP(((PySexpObject*)self));
  if (! sexp_self) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }
  
  SEXP sexp_other = RPY_SEXP(((PySexpObject*)other));
  if (! sexp_other) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }
  
  long same = (sexp_self == sexp_other);
  return PyBool_FromLong(same);
}
PyDoc_STRVAR(Sexp_rsame_doc,
             "Is the given object representing the same underlying R object as the instance.");

static PyObject*
Sexp_duplicate(PyObject *self, PyObject *kwargs)
{
  SEXP sexp_self, sexp_copy;
  PyObject *res;
  
  sexp_self = RPY_SEXP((PySexpObject*)self);
  if (! sexp_self) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;;
  }
  PROTECT(sexp_copy = Rf_duplicate(sexp_self));
  res = (PyObject *) newPySexpObject(sexp_copy);
  UNPROTECT(1);
  return res;
}
PyDoc_STRVAR(Sexp_duplicate_doc,
             "Makes a copy of the underlying Sexp object, and returns it.");

static PyObject*
Sexp___getstate__(PyObject *self)
{

  PyObject *res_string;

  SEXP sexp = RPY_SEXP((PySexpObject *)self);
  if (! sexp) {
    PyErr_Format(PyExc_ValueError, "NULL SEXP.");
    return NULL;
  }

  SEXP sexp_ser;
  PROTECT(sexp_ser = rpy_serialize(sexp, R_GlobalEnv));
  if (TYPEOF(sexp_ser) != RAWSXP) {
    UNPROTECT(1);
    PyErr_Format(PyExc_RuntimeError, 
                 "R's serialize did not return a raw vector.");
    return NULL;
  }
  /* PyByteArray is only available with Python >= 2.6 */
          /* res = PyByteArray_FromStringAndSize(sexp_ser, len); */

  /*FIXME: is this working on 64bit archs ? */
  res_string = PyString_FromStringAndSize((void *)RAW_POINTER(sexp_ser), 
                                          (Py_ssize_t)LENGTH(sexp_ser));
  UNPROTECT(1);
  return res_string;
}

PyDoc_STRVAR(Sexp___getstate___doc,
             "Returns a serialized object for the underlying R object");


static PyObject*
Sexp___setstate__(PyObject *self, PyObject *state)
{

  Py_INCREF(Py_None);
  return Py_None;

}

PyDoc_STRVAR(Sexp___setstate___doc,
             "set the state of an instance (dummy).");


static PyObject*
EmbeddedR_unserialize(PyObject* self, PyObject* args)
{
  PyObject *res;

  if (! (rpy_has_status(RPY_R_INITIALIZED))) {
    PyErr_Format(PyExc_RuntimeError, 
                 "R cannot evaluate code before being initialized.");
    return NULL;
  }
  

  char *raw;
  Py_ssize_t raw_size;
  int rtype;
  if (! PyArg_ParseTuple(args, "s#i",
                         &raw, &raw_size,
                         &rtype)) {
    return NULL;
  }

  if (rpy_has_status(RPY_R_BUSY)) {
    PyErr_Format(PyExc_RuntimeError, "Concurrent access to R is not allowed.");
    return NULL;
  }
  embeddedR_setlock();

  /* Not the most memory-efficient; an other option would
  * be to create a dummy RAW and rebind "raw" as its content
  * (wich seems clearly off the charts).
  */
  SEXP raw_sexp, sexp_ser;
  PROTECT(raw_sexp = NEW_RAW((int)raw_size));

  /*FIXME: use of the memcpy seems to point in the direction of
  * using the option mentioned above anyway. */
  Py_ssize_t raw_i;
  for (raw_i = 0; raw_i < raw_size; raw_i++) {
    RAW_POINTER(raw_sexp)[raw_i] = raw[raw_i];
  }
  PROTECT(sexp_ser = rpy_unserialize(raw_sexp, R_GlobalEnv));

  if (TYPEOF(sexp_ser) != rtype) {
    UNPROTECT(2);
    PyErr_Format(PyExc_ValueError, 
                 "Mismatch between the serialized object"
                 " and the expected R type"
                 " (expected %i but got %i)", rtype, TYPEOF(raw_sexp));
    return NULL;
  }
  res = (PyObject*)newPySexpObject(sexp_ser);
  
  UNPROTECT(2);
  embeddedR_freelock();
  return res;
}

static PyObject*
Sexp___reduce__(PyObject* self)
{
  PyObject *dict, *result;

  if (! (rpy_has_status(RPY_R_INITIALIZED))) {
    PyErr_Format(PyExc_RuntimeError, 
                 "R cannot evaluate code before being initialized.");
    return NULL;
  }
  
  dict = PyObject_GetAttrString((PyObject *)self,
                                "__dict__");
  if (dict == NULL) {
    PyErr_Clear();
    dict = Py_None;
    Py_INCREF(dict);
  }

  if (rpy_has_status(RPY_R_BUSY)) {
    PyErr_Format(PyExc_RuntimeError, "Concurrent access to R is not allowed.");
    return NULL;
  }
  embeddedR_setlock();

  result = Py_BuildValue("O(Oi)O",
                         rinterface_unserialize, /* constructor */
                         Sexp___getstate__(self),
                         TYPEOF(RPY_SEXP((PySexpObject *)self)),
                         dict);

  embeddedR_freelock();

  Py_DECREF(dict);
  return result;

}

PyDoc_STRVAR(Sexp___reduce___doc,
             "Prepare an instance for serialization.");



static PyMethodDef Sexp_methods[] = {
  {"do_slot", (PyCFunction)Sexp_do_slot, METH_O,
   Sexp_do_slot_doc},
  {"do_slot_assign", (PyCFunction)Sexp_do_slot_assign, METH_VARARGS,
   Sexp_do_slot_assign_doc},
  {"rsame", (PyCFunction)Sexp_rsame, METH_O,
   Sexp_rsame_doc},
  {"__deepcopy__", (PyCFunction)Sexp_duplicate, METH_KEYWORDS,
   Sexp_duplicate_doc},
  {"__getstate__", (PyCFunction)Sexp___getstate__, METH_NOARGS,
   Sexp___getstate___doc},
  {"__setstate__", (PyCFunction)Sexp___setstate__, METH_O,
   Sexp___setstate___doc},
  {"__reduce__", (PyCFunction)Sexp___reduce__, METH_NOARGS,
   Sexp___reduce___doc},
  {NULL, NULL}          /* sentinel */
};


static PyGetSetDef Sexp_getsets[] = {
  {"named", 
   (getter)Sexp_named_get,
   (setter)0,
   Sexp_named_doc},
  {"typeof", 
   (getter)Sexp_typeof_get,
   (setter)0,
   Sexp_typeof_doc},
  {"__sexp__",
   (getter)Sexp_sexp_get,
   (setter)Sexp_sexp_set,
   Sexp_sexp_doc},
  {"__sexp_refcount__",
   (getter)Sexp_refcount_get,
   (setter)0,
   Sexp_refcount_doc},
  {NULL, NULL, NULL, NULL}          /* sentinel */
};


static PyObject*
Sexp_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{

  PySexpObject *self = NULL;
  /* unsigned short int rpy_only = 1; */

  #ifdef RPY_VERBOSE
  printf("new '%s' object @...\n", type->tp_name);
  #endif 

  /* self = (PySexpObject *)PyObject_New(PySexpObject, type); */
  self = (PySexpObject *)type->tp_alloc(type, 0);
  #ifdef RPY_VERBOSE
  printf("  Python:%p / R:%p (R_NilValue) ...\n", self, R_NilValue);
  #endif 

  if (! self)
    PyErr_NoMemory();

  self->sObj = (SexpObject *)PyMem_Malloc(1 * sizeof(SexpObject));
  if (! self->sObj) {
    Py_DECREF(self);
    PyErr_NoMemory();
  }

  RPY_COUNT(self) = 1;
  RPY_SEXP(self) = R_NilValue;
  /* RPY_RPYONLY(self) = rpy_only; */

  #ifdef RPY_VERBOSE
  printf("done.\n");
  #endif 

  return (PyObject *)self;

}

static int
Sexp_init(PyObject *self, PyObject *args, PyObject *kwds)
{
#ifdef RPY_VERBOSE
  printf("Python:%p / R:%p - Sexp initializing...\n", 
         self, RPY_SEXP((PySexpObject *)self));
#endif 

  PyObject *sourceObject;

  PyObject *copy = Py_True;
  int sexptype = -1;
  SexpObject *tmpSexpObject;


  static char *kwlist[] = {"sexp", "sexptype", "copy", NULL};
  /* FIXME: handle the copy argument */

  /* the "sexptype" is as a quick hack to make calls from
   the constructor of SexpVector */
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "O|iO!", 
                                    kwlist,
                                    &sourceObject,
                                    &sexptype,
                                    &PyBool_Type, &copy)) {
    return -1;
  }

  if (! PyObject_IsInstance(sourceObject, 
                            (PyObject*)&Sexp_Type)) {
    PyErr_Format(PyExc_ValueError, 
                 "Can only instanciate from Sexp objects.");
    return -1;
  }

  if (PyObject_IsTrue(copy)) {
    tmpSexpObject = ((PySexpObject *)self)->sObj;
    if (tmpSexpObject != ((PySexpObject *)sourceObject)->sObj) {
      ((PySexpObject *)self)->sObj = ((PySexpObject *)sourceObject)->sObj;
      PyMem_Free(tmpSexpObject);
    }
    RPY_INCREF((PySexpObject *)self);
#ifdef RPY_VERBOSE
    printf("Python: %p / R: %p - sexp count is now %i.\n", 
           (PySexpObject *)self, RPY_SEXP((PySexpObject *)self), RPY_COUNT((PySexpObject *)self));
#endif 

  } else {
    PyErr_Format(PyExc_ValueError, "Cast without copy is not yet implemented.");
    return -1;
  }

#ifdef RPY_VERBOSE
  printf("done.\n");
#endif 

  /* SET_NAMED(RPY_SEXP((PySexpObject *)self), (unsigned int)2); */
  return 0;
}


/*
 * Generic Sexp_Type. It represents SEXP objects at large.
 */
static PyTypeObject Sexp_Type = {
        /* The ob_type field must be initialized in the module init function
         * to be portable to Windows without using C++. */
        PyObject_HEAD_INIT(NULL)
        0,                      /*ob_size*/
        "rpy2.rinterface.Sexp",      /*tp_name*/
        sizeof(PySexpObject),   /*tp_basicsize*/
        0,                      /*tp_itemsize*/
        /* methods */
        (destructor)Sexp_dealloc, /*tp_dealloc*/
        0,                      /*tp_print*/
        0,                      /*tp_getattr*/
        0,                      /*tp_setattr*/
        0,                      /*tp_compare*/
        Sexp_repr,              /*tp_repr*/
        0,                      /*tp_as_number*/
        0,                      /*tp_as_sequence*/
        0,                      /*tp_as_mapping*/
        0,                      /*tp_hash*/
        0,                      /*tp_call*/
        0,                      /*tp_str*/
        0,                      /*tp_getattro*/
        0,                      /*tp_setattro*/
        0,                      /*tp_as_buffer*/
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,     /*tp_flags*/
        0,                      /*tp_doc*/
        0,                      /*tp_traverse*/
        (inquiry)Sexp_clear,                      /*tp_clear*/
        0,                      /*tp_richcompare*/
        0,                      /*tp_weaklistoffset*/
        0,                      /*tp_iter*/
        0,                      /*tp_iternext*/
        Sexp_methods,           /*tp_methods*/
        0,                      /*tp_members*/
        Sexp_getsets,            /*tp_getset*/
        0,                      /*tp_base*/
        0,                      /*tp_dict*/
        0,                      /*tp_descr_get*/
        0,                      /*tp_descr_set*/
        0,                      /*tp_dictoffset*/
        (initproc)Sexp_init,    /*tp_init*/
        0,                      /*tp_alloc*/
        Sexp_new,               /*tp_new*/
        0,                      /*tp_free*/
        0,                      /*tp_is_gc*/
};


