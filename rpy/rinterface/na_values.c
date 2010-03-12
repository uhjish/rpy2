/* --- NA values --- */

PyDoc_STRVAR(NAInteger_Type_doc,
"Missing value for an integer in R."
);

static PyObject*
NAInteger_repr(PyObject *self)
{
  PyObject* repr = NULL;
  repr = PyString_FromString("NA_integer_");
  return repr;
}

static PyObject*
NA_str(PyObject *self)
{
  static PyObject* repr = NULL;
  if (repr == NULL) {
    repr = PyString_FromString("NA");
  }
  return repr;
}

/* Whenever an NA object is used for arithmetic or logic,
 * the results is NA. */
static PyObject*
NA_unaryfunc(PyObject *self)
{
  Py_XINCREF(self);
  return self;
}
static PyObject*
NA_binaryfunc(PyObject *self, PyObject *obj)
{
  Py_XINCREF(self);
  return self;

}
static PyObject*
NA_ternaryfunc(PyObject *self, PyObject *obj1, PyObject *obj2)
{
  Py_XINCREF(self);
  return self;
}

static int
NA_nonzero(PyObject *self)
{
  return 1;
}

static PyNumberMethods NAInteger_NumberMethods = {
  (binaryfunc)NA_binaryfunc, /* nb_add */
  (binaryfunc)NA_binaryfunc, /* nb_subtract; */
  (binaryfunc)NA_binaryfunc, /* nb_multiply; */
  (binaryfunc)NA_binaryfunc, /* nb_divide; */
  (binaryfunc)NA_binaryfunc, /* nb_remainder; */
  (binaryfunc)NA_binaryfunc, /* nb_divmod; */
  (ternaryfunc)NA_binaryfunc, /* nb_power; */
  (unaryfunc) NA_unaryfunc, /* nb_negative; */
  (unaryfunc) NA_unaryfunc, /* nb_positive; */
  (unaryfunc) NA_unaryfunc, /* nb_absolute; */
  (inquiry) NA_nonzero, /* nb_nonzero;       /* Used by PyObject_IsTrue */
  (unaryfunc) NA_unaryfunc, /* nb_invert; */
  (binaryfunc) NA_binaryfunc, /* nb_lshift; */
  (binaryfunc) NA_binaryfunc, /* nb_rshift; */
  (binaryfunc) NA_binaryfunc, /*  nb_and; */
  (binaryfunc) NA_binaryfunc, /*  nb_xor; */
  (binaryfunc) NA_binaryfunc, /* nb_or; */
  0, //(coerce) NA_coerce, /* coercion nb_coerce;       -- Used by the coerce() function */
  (unaryfunc) NA_unaryfunc, /* nb_int; */
  (unaryfunc) NA_unaryfunc, /* nb_long; */
  (unaryfunc) NA_unaryfunc, /* nb_float; */
  (unaryfunc) NA_unaryfunc, /* nb_oct; */
  (unaryfunc) NA_unaryfunc, /* nb_hex; */
  /* Added in release 2.0 */
  0, /* nb_inplace_add; */
  0, /* nb_inplace_subtract; */
  0, /* nb_inplace_multiply; */
  0, /* nb_inplace_divide; */
  0, /* nb_inplace_remainder; */
  0, /* nb_inplace_power; */
  0, /* nb_inplace_lshift; */
  0, /* nb_inplace_rshift; */
  0, /* nb_inplace_and; */
  0, /* nb_inplace_xor; */
  0, /* nb_inplace_or; */
  /* Added in release 2.2 */
  (binaryfunc) NA_binaryfunc, /* nb_floor_divide; */
  (binaryfunc) NA_binaryfunc, /* nb_true_divide; */
  0, /* nb_inplace_floor_divide; */
  0, /* nb_inplace_true_divide; */
  /* Added in release 2.5 */
#if PY_VERSION_HEX >= 0x02050000
  (unaryfunc) NA_unaryfunc /* nb_index; */
#endif
};


static PyObject*
NAInteger_tp_new(PyTypeObject *type, PyObject *args, PyObject *kwds);


static PyTypeObject NAInteger_Type = {
        /* The ob_type field must be initialized in the module init function
         * to be portable to Windows without using C++. */
        PyObject_HEAD_INIT(NULL)
        0,                      /*ob_size*/
        "rpy2.rinterface.NAIntegerType",       /*tp_name*/
        sizeof(PyObject),   /*tp_basicsize*/
        0,                      /*tp_itemsize*/
        /* methods */
        0, /*tp_dealloc*/
        0,                      /*tp_print*/
        0,                      /*tp_getattr*/
        0,                      /*tp_setattr*/
        0,                      /*tp_compare*/
        NAInteger_repr,                      /*tp_repr*/
        &NAInteger_NumberMethods,                      /*tp_as_number*/
        0,                      /*tp_as_sequence*/
        0,                      /*tp_as_mapping*/
        0,                      /*tp_hash*/
        0,                      /*tp_call*/
        NA_str,                      /*tp_str*/
        0,                      /*tp_getattro*/
        0,                      /*tp_setattro*/
        0,                      /*tp_as_buffer*/
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
        NAInteger_Type_doc,                      /*tp_doc*/
        0,                      /*tp_traverse*/
        0,                      /*tp_clear*/
        0,                      /*tp_richcompare*/
        0,                      /*tp_weaklistoffset*/
        0,                      /*tp_iter*/
        0,                      /*tp_iternext*/
        0,                      /*tp_methods*/
        0,                      /*tp_members*/
        0,                      /*tp_getset*/
        &PyLong_Type,             /*tp_base*/
        0,                      /*tp_dict*/
        0,                      /*tp_descr_get*/
        0,                      /*tp_descr_set*/
        0,                      /*tp_dictoffset*/
        0, //(initproc)ClosureSexp_init,                      /*tp_init*/
        0,                      /*tp_alloc*/
        NAInteger_tp_new,                      /*tp_new*/
        0,                      /*tp_free*/
        0                      /*tp_is_gc*/
};

static PyObject*
NAInteger_tp_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  RPY_NA_TP_NEW("NAIntegerType", PyLong_Type, PyLong_FromLong, 
                (long)NA_INTEGER)
}

static PyObject*
NAInteger_New(int new)
{
  RPY_NA_NEW(NAInteger_Type, NAInteger_tp_new)
}

/* NA Boolean / Logical */

PyDoc_STRVAR(NALogical_Type_doc,
"Missing value for a boolean in R."
);

static PyObject*
NALogical_tp_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  RPY_NA_TP_NEW("NALogicalType", PyLong_Type, PyLong_FromLong, 
                (long)NA_LOGICAL)
}

static PyObject*
NALogical_New(int new)
{
  RPY_NA_NEW(NALogical_Type, NALogical_tp_new)
}

static PyObject*
NALogical_repr(PyObject *self)
{
  static PyObject* repr = NULL;
  if (repr == NULL) {
    repr = PyString_FromString("NA");
  }
  Py_XINCREF(repr);
  return repr;
}

static PyNumberMethods NALogical_NumberMethods = {
  0, /* nb_add */
  0, /* nb_subtract; */
  0, /* nb_multiply; */
  0, /* nb_divide; */
  0, /* nb_remainder; */
  0, /* nb_divmod; */
  0, /* nb_power; */
  0, /* nb_negative; */
  0, /* nb_positive; */
  0, /* nb_absolute; */
  0, /* nb_nonzero;       /* Used by PyObject_IsTrue */
  0, /* nb_invert; */
  0, /* nb_lshift; */
  0, /* nb_rshift; */
  (binaryfunc) NA_binaryfunc, /*  nb_and; */
  (binaryfunc) NA_binaryfunc, /*  nb_xor; */
  (binaryfunc) NA_binaryfunc, /* nb_or; */
  0, //(coerce) NA_coerce, /* coercion nb_coerce;       -- Used by the coerce() function */
  0, /* nb_int; */
  0, /* nb_long; */
  0, /* nb_float; */
  0, /* nb_oct; */
  0, /* nb_hex; */
  /* Added in release 2.0 */
  0, /* nb_inplace_add; */
  0, /* nb_inplace_subtract; */
  0, /* nb_inplace_multiply; */
  0, /* nb_inplace_divide; */
  0, /* nb_inplace_remainder; */
  0, /* nb_inplace_power; */
  0, /* nb_inplace_lshift; */
  0, /* nb_inplace_rshift; */
  0, /* nb_inplace_and; */
  0, /* nb_inplace_xor; */
  0, /* nb_inplace_or; */
  /* Added in release 2.2 */
  0, /* nb_floor_divide; */
  0, /* nb_true_divide; */
  0, /* nb_inplace_floor_divide; */
  0, /* nb_inplace_true_divide; */
  /* Added in release 2.5 */
#if PY_VERSION_HEX >= 0x02050000
  0 /* nb_index; */
#endif
};

static PyTypeObject NALogical_Type = {
        /* The ob_type field must be initialized in the module init function
         * to be portable to Windows without using C++. */
        PyObject_HEAD_INIT(NULL)
        0,                      /*ob_size*/
        "rpy2.rinterface.NALogicalType",       /*tp_name*/
        sizeof(PyObject),   /*tp_basicsize*/
        0,                      /*tp_itemsize*/
        /* methods */
        0, /*tp_dealloc*/
        0,                      /*tp_print*/
        0,                      /*tp_getattr*/
        0,                      /*tp_setattr*/
        0,                      /*tp_compare*/
        NALogical_repr,                      /*tp_repr*/
        &NALogical_NumberMethods,                      /*tp_as_number*/
        0,                      /*tp_as_sequence*/
        0,                      /*tp_as_mapping*/
        0,                      /*tp_hash*/
        0,                      /*tp_call*/
        NA_str,                      /*tp_str*/
        0,                      /*tp_getattro*/
        0,                      /*tp_setattro*/
        0,                      /*tp_as_buffer*/
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
        NALogical_Type_doc,                      /*tp_doc*/
        0,                      /*tp_traverse*/
        0,                      /*tp_clear*/
        0,                      /*tp_richcompare*/
        0,                      /*tp_weaklistoffset*/
        0,                      /*tp_iter*/
        0,                      /*tp_iternext*/
        0, //NAInteger_methods,           /*tp_methods*/
        0,                      /*tp_members*/
        0,                      /*tp_getset*/
        &PyLong_Type,             /*tp_base*/
        0,                      /*tp_dict*/
        0,                      /*tp_descr_get*/
        0,                      /*tp_descr_set*/
        0,                      /*tp_dictoffset*/
        0, //(initproc)ClosureSexp_init,                      /*tp_init*/
        0,                      /*tp_alloc*/
        NALogical_tp_new,                      /*tp_new*/
        0,                      /*tp_free*/
        0                      /*tp_is_gc*/
};

/* NA Float / Real */

PyDoc_STRVAR(NAReal_Type_doc,
"Missing value for a float in R."
);

static PyObject*
NAReal_tp_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  RPY_NA_TP_NEW("NARealType", PyFloat_Type, PyFloat_FromDouble, 
                (long)NA_REAL)
}

static PyObject*
NAReal_New(int new)
{
  RPY_NA_NEW(NAReal_Type, NAReal_tp_new)
}

static PyObject*
NAReal_repr(PyObject *self)
{
  static PyObject* repr = NULL;
  if (repr == NULL) {
    repr = PyString_FromString("NA_real_");
  }
  Py_XINCREF(repr);
  return repr;
}


static PyNumberMethods NAReal_NumberMethods = {
  (binaryfunc)NA_binaryfunc, /* nb_add */
  (binaryfunc)NA_binaryfunc, /* nb_subtract; */
  (binaryfunc)NA_binaryfunc, /* nb_multiply; */
  (binaryfunc)NA_binaryfunc, /* nb_divide; */
  (binaryfunc)NA_binaryfunc, /* nb_remainder; */
  (binaryfunc)NA_binaryfunc, /* nb_divmod; */
  (ternaryfunc)NA_binaryfunc, /* nb_power; */
  (unaryfunc) NA_unaryfunc, /* nb_negative; */
  (unaryfunc) NA_unaryfunc, /* nb_positive; */
  (unaryfunc) NA_unaryfunc, /* nb_absolute; */
  (inquiry) NA_nonzero, /* nb_nonzero;       /* Used by PyObject_IsTrue */
  0, /* nb_invert; */
  0, /* nb_lshift; */
  0, /* nb_rshift; */
  0, /*  nb_and; */
  0, /*  nb_xor; */
  0, /* nb_or; */
  0, //(coerce) NA_coerce, /* coercion nb_coerce;       -- Used by the coerce() function */
  (unaryfunc) NA_unaryfunc, /* nb_int; */
  (unaryfunc) NA_unaryfunc, /* nb_long; */
  (unaryfunc) NA_unaryfunc, /* nb_float; */
  0, /* nb_oct; */
  0, /* nb_hex; */
  /* Added in release 2.0 */
  0, /* nb_inplace_add; */
  0, /* nb_inplace_subtract; */
  0, /* nb_inplace_multiply; */
  0, /* nb_inplace_divide; */
  0, /* nb_inplace_remainder; */
  0, /* nb_inplace_power; */
  0, /* nb_inplace_lshift; */
  0, /* nb_inplace_rshift; */
  0, /* nb_inplace_and; */
  0, /* nb_inplace_xor; */
  0, /* nb_inplace_or; */
  /* Added in release 2.2 */
  (binaryfunc) NA_binaryfunc, /* nb_floor_divide; */
  (binaryfunc) NA_binaryfunc, /* nb_true_divide; */
  0, /* nb_inplace_floor_divide; */
  0, /* nb_inplace_true_divide; */
  /* Added in release 2.5 */
#if PY_VERSION_HEX >= 0x02050000
  0 /* nb_index; */
#endif
};


static PyTypeObject NAReal_Type = {
        /* The ob_type field must be initialized in the module init function
         * to be portable to Windows without using C++. */
        PyObject_HEAD_INIT(NULL)
        0,                      /*ob_size*/
        "rpy2.rinterface.NARealType",       /*tp_name*/
        sizeof(PyObject),   /*tp_basicsize*/
        0,                      /*tp_itemsize*/
        /* methods */
        0, /*tp_dealloc*/
        0,                      /*tp_print*/
        0,                      /*tp_getattr*/
        0,                      /*tp_setattr*/
        0,                      /*tp_compare*/
        NAReal_repr,                      /*tp_repr*/
        &NAReal_NumberMethods,                      /*tp_as_number*/
        0,                      /*tp_as_sequence*/
        0,                      /*tp_as_mapping*/
        0,                      /*tp_hash*/
        0,                      /*tp_call*/
        NA_str,                      /*tp_str*/
        0,                      /*tp_getattro*/
        0,                      /*tp_setattro*/
        0,                      /*tp_as_buffer*/
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
        NAReal_Type_doc,                      /*tp_doc*/
        0,                      /*tp_traverse*/
        0,                      /*tp_clear*/
        0,                      /*tp_richcompare*/
        0,                      /*tp_weaklistoffset*/
        0,                      /*tp_iter*/
        0,                      /*tp_iternext*/
        0, //NAInteger_methods,           /*tp_methods*/
        0,                      /*tp_members*/
        0,                      /*tp_getset*/
        &PyFloat_Type,             /*tp_base*/
        0,                      /*tp_dict*/
        0,                      /*tp_descr_get*/
        0,                      /*tp_descr_set*/
        0,                      /*tp_dictoffset*/
        0, //(initproc)ClosureSexp_init,                      /*tp_init*/
        0,                      /*tp_alloc*/
        NAReal_tp_new,                      /*tp_new*/
        0,                      /*tp_free*/
        0                      /*tp_is_gc*/
};

/* NA Float / Real */

PyDoc_STRVAR(NACharacter_Type_doc,
"Missing value for a string."
);

static PyObject*
NACharacter_tp_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  RPY_NA_TP_NEW("NACharacterType", PyString_Type, PyString_FromString, "")
}

static PyObject*
NACharacter_New(int new)
{
  RPY_NA_NEW(NACharacter_Type, NACharacter_tp_new)
}


static PyObject*
NACharacter_repr(PyObject *self)
{
  static PyObject* repr = NULL;
  if (repr == NULL) {
    repr = PyString_FromString("NA_character_");
  }
  Py_XINCREF(repr);
  return repr;
}


static PyTypeObject NACharacter_Type = {
        /* The ob_type field must be initialized in the module init function
         * to be portable to Windows without using C++. */
        PyObject_HEAD_INIT(NULL)
        0,                      /*ob_size*/
        "rpy2.rinterface.NACharacterType",       /*tp_name*/
        sizeof(PyObject),   /*tp_basicsize*/
        0,                      /*tp_itemsize*/
        /* methods */
        0, /*tp_dealloc*/
        0,                      /*tp_print*/
        0,                      /*tp_getattr*/
        0,                      /*tp_setattr*/
        0,                      /*tp_compare*/
        NACharacter_repr,                      /*tp_repr*/
        0,                      /*tp_as_number*/
        0,                      /*tp_as_sequence*/
        0,                      /*tp_as_mapping*/
        0,                      /*tp_hash*/
        0,                      /*tp_call*/
        NA_str,                      /*tp_str*/
        0,                      /*tp_getattro*/
        0,                      /*tp_setattro*/
        0,                      /*tp_as_buffer*/
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
        NACharacter_Type_doc,                      /*tp_doc*/
        0,                      /*tp_traverse*/
        0,                      /*tp_clear*/
        0,                      /*tp_richcompare*/
        0,                      /*tp_weaklistoffset*/
        0,                      /*tp_iter*/
        0,                      /*tp_iternext*/
        0, //NAInteger_methods,           /*tp_methods*/
        0,                      /*tp_members*/
        0,                      /*tp_getset*/
        &PyString_Type,             /*tp_base*/
        0,                      /*tp_dict*/
        0,                      /*tp_descr_get*/
        0,                      /*tp_descr_set*/
        0,                      /*tp_dictoffset*/
        0, //(initproc)ClosureSexp_init,                      /*tp_init*/
        0,                      /*tp_alloc*/
        NACharacter_tp_new,                      /*tp_new*/
        0,                      /*tp_free*/
        0                      /*tp_is_gc*/
};



/* Missing parameter value (not an NA in the usual sense) */

PyDoc_STRVAR(Missing_Type_doc,
"Missing parameter (in a function call)."
);

static PyObject*
MissingType_tp_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  static PySexpObject *self = NULL;
  static char *kwlist[] = {0};

  if (! PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist)) {
    return NULL;
  }

  if (self == NULL) {
    self = (PySexpObject*)(Sexp_Type.tp_new(type, Py_None, Py_None));
    if (self == NULL) {
      return NULL;
    }
  }
  Py_XINCREF(self);
  return (PyObject *)self;
}

static PyObject*
MissingType_tp_init(PyObject *self, PyObject *args, PyObject *kwds)
{
  static char *kwlist[] = {0};
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist)) {
    return NULL;
  }
  return 0;
}

static PyObject*
MissingType_repr(PyObject *self)
{
  static PyObject* repr = NULL;
  if (repr == NULL) {
    repr = PyString_FromString("Missing");
  }
  Py_XINCREF(repr);
  return repr;
}

static PyObject*
MissingType_str(PyObject *self)
{
  static PyObject* repr = NULL;
  if (repr == NULL) {
    repr = PyString_FromString("Missing");
  }
  Py_XINCREF(repr);
  return repr;
}

static PyTypeObject Missing_Type = {
        /* The ob_type field must be initialized in the module init function
         * to be portable to Windows without using C++. */
        PyObject_HEAD_INIT(NULL)
        0,                      /*ob_size*/
        "rpy2.rinterface.MissingType",       /*tp_name*/
        sizeof(PySexpObject),   /*tp_basicsize*/
        0,                      /*tp_itemsize*/
        /* methods */
        0, /*tp_dealloc*/
        0,                      /*tp_print*/
        0,                      /*tp_getattr*/
        0,                      /*tp_setattr*/
        0,                      /*tp_compare*/
        MissingType_repr,                      /*tp_repr*/
        0,                      /*tp_as_number*/
        0,                      /*tp_as_sequence*/
        0,                      /*tp_as_mapping*/
        0,                      /*tp_hash*/
        0,                      /*tp_call*/
        MissingType_str,                      /*tp_str*/
        0,                      /*tp_getattro*/
        0,                      /*tp_setattro*/
        0,                      /*tp_as_buffer*/
        Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE|Py_TPFLAGS_CHECKTYPES, /*tp_flags*/
        Missing_Type_doc,                      /*tp_doc*/
        0,                      /*tp_traverse*/
        0,                      /*tp_clear*/
        0,                      /*tp_richcompare*/
        0,                      /*tp_weaklistoffset*/
        0,                      /*tp_iter*/
        0,                      /*tp_iternext*/
        0, //NAInteger_methods,           /*tp_methods*/
        0,                      /*tp_members*/
        0,                      /*tp_getset*/
        &Sexp_Type,             /*tp_base*/
        0,                      /*tp_dict*/
        0,                      /*tp_descr_get*/
        0,                      /*tp_descr_set*/
        0,                      /*tp_dictoffset*/
        MissingType_tp_init,                      /*tp_init*/
        0,                      /*tp_alloc*/
        MissingType_tp_new,                      /*tp_new*/
        0,                      /*tp_free*/
        0                      /*tp_is_gc*/
};
