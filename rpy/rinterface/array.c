/* A. Belopolsky's Array interface */


#include <Python.h>
#include <Rdefines.h>
#include <Rinternals.h>
#include "rpy_rinterface.h"

#define ARRAY_INTERFACE_VERSION 2

/* Array Interface flags */
#define NPY_CONTIGUOUS    0x0001
#define NPY_FORTRAN       0x0002
#define NPY_ENSURECOPY    0x0020
#define NPY_ALIGNED       0x0100
#define NPY_NOTSWAPPED    0x0200
#define NPY_WRITEABLE     0x0400
#define NPY_BEHAVED       (NPY_ALIGNED | NPY_WRITEABLE)
#define NPY_FARRAY        (NPY_FORTRAN | NPY_BEHAVED)

typedef struct {
  int version;
  int nd;
  char typekind;
  int itemsize;
  int flags;
  Py_intptr_t *shape;
  Py_intptr_t *strides;
  void *data;
} PyArrayInterface;

static char
sexp_typekind(SEXP sexp)
{
  /* Given an SEXP object, this returns the corresponding
   * Type in the numpy world.
   */
  switch (TYPEOF(sexp)) {
  case REALSXP: return 'f';
  case INTSXP: return 'i';
    /* FIXME: handle strings ? */
    /* case STRSXP: return 'S'; */
    /* FIXME: handle 'O' (as R list ?) */
  case CPLXSXP: return 'c';
    /* It would be more logical (hah) to return 'b' here, but 1) R booleans are
     * full integer width, and Numpy for example can only handle 8-bit booleans,
     * not 32-bit, 2) R actually uses this width; NA_LOGICAL is the same as
     * NA_INTEGER, i.e. INT_MIN, i.e. 0x80000000. So this also lets us preserve
     * NA's: */
  case LGLSXP: return 'i';
  }
  return 0;
}

static void*
sexp_typepointer(SEXP sexp)
{
  switch (TYPEOF(sexp)) {
  case REALSXP: return (void *)NUMERIC_POINTER(sexp);
  case INTSXP: return (void *)INTEGER_POINTER(sexp);
    /* case STRSXP: return (void *)CHARACTER_POINTER(; */
  case CPLXSXP: return (void *)COMPLEX_POINTER(sexp);
  case LGLSXP: return (void *)LOGICAL_POINTER(sexp);
  }
  return NULL;
}


static int
sexp_itemsize(SEXP sexp)
{
  switch (TYPEOF(sexp)) {
  case REALSXP: return sizeof(*REAL(sexp));
  case INTSXP: return sizeof(*INTEGER(sexp));
  case STRSXP: return sizeof(*CHAR(sexp));
  case CPLXSXP: return sizeof(*COMPLEX(sexp));
  case LGLSXP: return sizeof(*LOGICAL(sexp));
  }
  return 0;
}

static int
sexp_rank(SEXP sexp)
{
  /* Return the number of dimensions for the array 
   * (e.g., a vector will return 1, a matrix 2, ...)
   */
  SEXP dim = getAttrib(sexp, R_DimSymbol);
  if (dim == R_NilValue)
    return 1;
  return GET_LENGTH(dim);
}

static void
sexp_shape(SEXP sexp, Py_intptr_t* shape, int nd)
{
  /* Set the numpy 'shape', that is a vector of Py_intptr_t
   * containing the size of each dimension (see sexp_rank).
   */
  int i;
  SEXP dim = getAttrib(sexp, R_DimSymbol);
  if (dim == R_NilValue)
    shape[0] = LENGTH(sexp);
  else for (i = 0; i < nd; ++i) {
      shape[i] = INTEGER(dim)[i];
    }
}

static void
array_struct_free(void *ptr, void *arr)
{
  PyArrayInterface *inter       = (PyArrayInterface *)ptr;
  PyMem_Free(inter->shape);
  Py_DECREF((PyObject *)arr);
  PyMem_Free(inter);
}


PyObject* 
array_struct_get(PySexpObject *self)
{
  /* Get an array structure as understood by the numpy package from
     'self' (a SexpVector).
   */
  SEXP sexp = RPY_SEXP(self);
  if (!sexp) {
    PyErr_SetString(PyExc_AttributeError, "Null sexp");
    return NULL;
  }

  char typekind =  sexp_typekind(sexp);
  if (!typekind) {
    PyErr_SetString(PyExc_AttributeError, "Unsupported SEXP type");
    return NULL;
  }

  /* allocate memory for the array description (this is what will be returned) */
  PyArrayInterface *inter;
  inter = (PyArrayInterface *)PyMem_Malloc(sizeof(PyArrayInterface));
  if (!inter) {
    return PyErr_NoMemory();
  }

  inter->version = ARRAY_INTERFACE_VERSION;

  int nd = sexp_rank(sexp);
  inter->nd = nd;

  inter->typekind = typekind;
  inter->itemsize = sexp_itemsize(sexp);
  inter->flags = NPY_FARRAY;
  inter->shape = (Py_intptr_t*)PyMem_Malloc(sizeof(Py_intptr_t)*nd*2);
  sexp_shape(sexp, inter->shape, nd);
  inter->strides = inter->shape + nd;
  Py_intptr_t stride = inter->itemsize;
  inter->strides[0] = stride;

  int i;
  for (i = 1; i < nd; ++i) {
    stride *= inter->shape[i-1];
    inter->strides[i] = stride;
  }
  inter->data = sexp_typepointer(sexp);
  if (inter->data == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Error while mapping type.");
    return NULL;
  }
  Py_INCREF(self);
  return PyCObject_FromVoidPtrAndDesc(inter, self, array_struct_free);
}

