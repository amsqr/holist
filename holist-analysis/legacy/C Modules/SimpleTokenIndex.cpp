/* Example of embedding Python in another program */

#include <Python.h>
#include "structmember.h"

#include <list>
#include <tr1/unordered_map>
#include <tr1/unordered_set>


PyMODINIT_FUNC initSimpleTokenIndex(void); /* Forward */



// should be self sorting (insertion sort) and limits length


    
typedef ::std::tr1::unordered_map<int, ::std::tr1::unordered_set<int> > MapIndex;

// on insert (of similarity entry): 
//    retrieve IndexRow for first document Id
//    iterate through similarities, insert if new_similarity is greater than existing (then according to IndexRow insert)
//    repeat for second docId, if it doesn't exist, add IndexRow for it and insert similarityEntry

// query: look up docid, return list.
typedef struct {
    PyObject_HEAD
    MapIndex index;
} SimpleTokenIndex;



static PyObject* SimpleTokenIndex_Index(PyObject *self, PyObject* args)
{
	return self;
	//return PyInt_FromLong(42L);
}

static void SimpleTokenIndex_dealloc(SimpleTokenIndex* self)
{
    self->ob_type->tp_free((PyObject*)self);
}


static PyObject *
SimpleTokenIndex_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    SimpleTokenIndex *self;

    self = (SimpleTokenIndex *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->index = ::std::tr1::unordered_map<int, ::std::tr1::unordered_set<int> >();
    }

    return (PyObject *)self;
}

static int
SimpleTokenIndex_init(SimpleTokenIndex *self, PyObject *args, PyObject *kwds)
{
    
    return 0;
}

static PyMemberDef SimpleTokenIndex_members[] = {
    {NULL}  /* Sentinel */
};

static PyObject *
SimpleTokenIndex_insert(SimpleTokenIndex* self, PyObject *args, PyObject *kwds)
{
	// parse input (first id, second id, similarity)
	int id1, id2;
    if (! PyArg_ParseTuple(args,"ii", &id1, &id2)){
        return NULL; 
    }
    
    MapIndex::iterator rowIt = self->index.find(id1);
    if(rowIt != self->index.end()){
    	::std::tr1::unordered_set<int> &row = rowIt->second;
        row.insert(id2);
    } else{
    	//we aren't tracking id1 at all yet, let's insert a row for it.
    	::std::tr1::unordered_set<int> row;
    	row.insert(id2);
    	std::pair<int,::std::tr1::unordered_set<int> > pairEntry (id1,row);
    	self->index.insert(pairEntry);
    }
    
    //return success
    Py_RETURN_NONE;
}


static PyObject *
SimpleTokenIndex_query(SimpleTokenIndex* self, PyObject *args, PyObject *kwds)
{
	// parse input (first id, second id, similarity)
    PyObject* obj;
    //PyObject* seq;

    ::std::tr1::unordered_set<int> results;
	//static char *kwlist[] = {"documentId", NULL};
    if (! PyArg_ParseTuple(args, "O", &obj)){
        return NULL; 
    }
    
    int i, len; 
    //seq = PySequence_Fast(obj, "expected a sequence");
    len = PySequence_Size(obj);
    for (i = 0; i < len; i++) {

        long lid = PyInt_AsLong(PyList_GetItem(obj, i));
        MapIndex::const_iterator rowIt = self->index.find(lid);
        if(rowIt != self->index.end()){
            const ::std::tr1::unordered_set<int> &row = rowIt->second;
            results.insert(row.begin(), row.end());
        }

    }
    //Py_DECREF(seq);
    //; // HA! GC that

    PyObject* resultList = PyList_New(0);
    //build python list
    for (::std::tr1::unordered_set<int>::const_iterator it = results.begin(); it != results.end(); ++it)
    {
        PyObject* val = Py_BuildValue("i",*it);
    	PyList_Append(resultList, val);
        Py_DECREF(val);
    }
    Py_DECREF(obj);
    //return list
    return resultList;
}

static PyObject *
SimpleTokenIndex_getAllIds(SimpleTokenIndex* self, PyObject *args, PyObject *kwds)
{
    PyObject* resultList = PyList_New(0);
    //build python list
    for (::std::tr1::unordered_map<int, ::std::tr1::unordered_set<int> >::const_iterator it = self->index.begin(); it != self->index.end(); ++it)
    {
        PyList_Append(resultList,Py_BuildValue("i",it->first));
    }
    //return list
    return resultList;
}


static PyMethodDef SimpleTokenIndex_methods[] = {
    {"insert", (PyCFunction)SimpleTokenIndex_insert, METH_VARARGS,
     "For a term, insert a docID."
    },
    {"query", (PyCFunction)SimpleTokenIndex_query, METH_VARARGS,
     "Query documents for a term id."
    },
    {"getAllIds", (PyCFunction)SimpleTokenIndex_getAllIds, METH_NOARGS,
     "Get a list of all Ids."
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject SimpleTokenIndexType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "fwi.SimpleTokenIndex",     /*tp_name*/
    sizeof(SimpleTokenIndex),   /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)SimpleTokenIndex_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "SimpleTokenIndex objects", /* tp_doc */
    0,		                   /* tp_traverse */
    0,		                   /* tp_clear */
    0,		                   /* tp_richcompare */
    0,		                   /* tp_weaklistoffset */
    0,		                   /* tp_iter */
    0,		                   /* tp_iternext */
    SimpleTokenIndex_methods,   /* tp_methods */
    SimpleTokenIndex_members,   /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)SimpleTokenIndex_init,      /* tp_init */
    0,                         /* tp_alloc */
    SimpleTokenIndex_new,       /* tp_new */
};


static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initSimpleTokenIndex(void) 
{
    PyObject* m;

    if (PyType_Ready(&SimpleTokenIndexType) < 0)
        return;

    m = Py_InitModule3("SimpleTokenIndex", module_methods,
                       "SimpleTokenIndex module.");

    if (m == NULL)
      return;

    Py_INCREF(&SimpleTokenIndexType);
    PyModule_AddObject(m, "SimpleTokenIndex", (PyObject *)&SimpleTokenIndexType);
}

