/* Example of embedding Python in another program */

#include <Python.h>
#include "structmember.h"

#include <list>
#include <tr1/unordered_map>


PyMODINIT_FUNC initFixedWidthIndex(void); /* Forward */

struct SimilarityEntry{
	int documentId;
	double similarity;
};

// should be self sorting (insertion sort) and limits length
// if length > maxWidth: pop_back
typedef struct {
    std::list<SimilarityEntry> values;
    int _size;
} IndexRow;
typedef ::std::tr1::unordered_map<int, IndexRow> MapIndex;

// on insert (of similarity entry): 
//    retrieve IndexRow for first document Id
//    iterate through similarities, insert if new_similarity is greater than existing (then according to IndexRow insert)
//    repeat for second docId, if it doesn't exist, add IndexRow for it and insert similarityEntry

// query: look up docid, return list.
typedef struct {
    PyObject_HEAD
    MapIndex index;
    int maxWidth;
} FixedWidthIndex;



static PyObject* FixedWidthIndex_Index(PyObject *self, PyObject* args)
{
	return self;
	//return PyInt_FromLong(42L);
}

static void FixedWidthIndex_dealloc(FixedWidthIndex* self)
{
    self->ob_type->tp_free((PyObject*)self);
}


static PyObject *
FixedWidthIndex_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    FixedWidthIndex *self;

    self = (FixedWidthIndex *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->index = ::std::tr1::unordered_map<int, IndexRow>();
        self->maxWidth = 0;
    }

    return (PyObject *)self;
}

static int
FixedWidthIndex_init(FixedWidthIndex *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"maxWidth", NULL};
    if (! PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &self->maxWidth)){
        return -1; 
    }

    return 0;
}

static PyMemberDef FixedWidthIndex_members[] = {
    {"maxWidth", T_INT, offsetof(FixedWidthIndex, maxWidth), 0,
     "maximum width of index number"},
    {NULL}  /* Sentinel */
};

static PyObject *
FixedWidthIndex_insert(FixedWidthIndex* self, PyObject *args, PyObject *kwds)
{
	// parse input (first id, second id, similarity)
	int id1, id2;
    double similarity;
	//static char *kwlist[] = {"documentId", "comparedToId", "similarity", NULL};
    //static char *kwlist[] = {"documentId", NULL};
    //if (! PyArg_ParseTupleAndKeywords(args, kwds, "i", kwlist, &test)) {//, &id2, &similarity)){
     //   printf("NULL THAT SHIT..\n");
    if (! PyArg_ParseTuple(args,"iid", &id1, &id2, &similarity)){
        return NULL; 
    }
    // create entry object
    SimilarityEntry entry;
    entry.documentId = id2;
    entry.similarity = similarity;
    // insert into index
    //find row for id1
    
    MapIndex::iterator rowIt = self->index.find(id1);
    if(rowIt != self->index.end()){
    	IndexRow &row = rowIt->second;
    	if(similarity > row.values.back().similarity || row._size < self->maxWidth){
            
    		//iterate through and insert appropriately
            bool inserted = false;
            std::list<SimilarityEntry>::iterator iterator;
            for (iterator = row.values.begin(); iterator != row.values.end(); ++iterator) {
                if(iterator->similarity <= entry.similarity){
                    row.values.insert(iterator, entry); // insert sorted
                    row._size++;
                    inserted = true;
                    break; // we're done
                }
            }
            if(!inserted){
                row.values.push_back(entry);
                row._size++;
            }
            if(row._size > self->maxWidth){
                row.values.pop_back(); // limit size by removing least similar entry
                row._size--;
            }
    	}
    } else{
    	//we aren't tracking id1 at all yet, let's insert a row for it.
    	IndexRow row;
    	row.values.push_back(entry);
        row._size = 1;
    	std::pair<int,IndexRow> pairEntry (id1,row);
    	self->index.insert(pairEntry);
    }
    
    //return success
    Py_RETURN_NONE;
}

static PyObject *
FixedWidthIndex_query(FixedWidthIndex* self, PyObject *args, PyObject *kwds)
{
	// parse input (first id, second id, similarity)
	int id;
	//static char *kwlist[] = {"documentId", NULL};
    if (! PyArg_ParseTuple(args, "i", &id)){
        return NULL; 
    }

    //find row for id1
    MapIndex::const_iterator rowIt = self->index.find(id);
    if(rowIt == self->index.end()){
    	Py_RETURN_FALSE;
    }
    const IndexRow &row = rowIt->second;

    PyObject* resultList = PyList_New(0);
    //build python list
    for (std::list<SimilarityEntry>::const_iterator it = row.values.begin(); it != row.values.end(); ++it)
    {
        PyObject* val = Py_BuildValue("(i,d)",it->documentId, it->similarity);
    	PyList_Append(resultList, val);
        Py_DECREF(val);
        //PyList_Append(resultList,Py_BuildValue("(i,d)",it->documentId, it->similarity));
    }
    //return list
    return resultList;
}

static PyObject *
FixedWidthIndex_getAllIds(FixedWidthIndex* self, PyObject *args, PyObject *kwds)
{
    PyObject* resultList = PyList_New(0);
    //build python list
    for (::std::tr1::unordered_map<int, IndexRow>::const_iterator it = self->index.begin(); it != self->index.end(); ++it)
    {
        PyList_Append(resultList,Py_BuildValue("i",it->first));
    }
    //return list
    return resultList;
}

static PyMethodDef FixedWidthIndex_methods[] = {
    {"insert", (PyCFunction)FixedWidthIndex_insert, METH_VARARGS,
     "Insert a similarity measurement to the index."
    },
    {"query", (PyCFunction)FixedWidthIndex_query, METH_VARARGS,
     "Query top similar documents for an id."
    },
    {"getAllIds", (PyCFunction)FixedWidthIndex_getAllIds, METH_NOARGS,
     "Get a list of all Ids."
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject FixedWidthIndexType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "fwi.FixedWidthIndex",     /*tp_name*/
    sizeof(FixedWidthIndex),   /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)FixedWidthIndex_dealloc, /*tp_dealloc*/
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
    "FixedWidthIndex objects", /* tp_doc */
    0,		                   /* tp_traverse */
    0,		                   /* tp_clear */
    0,		                   /* tp_richcompare */
    0,		                   /* tp_weaklistoffset */
    0,		                   /* tp_iter */
    0,		                   /* tp_iternext */
    FixedWidthIndex_methods,   /* tp_methods */
    FixedWidthIndex_members,   /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)FixedWidthIndex_init,      /* tp_init */
    0,                         /* tp_alloc */
    FixedWidthIndex_new,       /* tp_new */
};


static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initFixedWidthIndex(void) 
{
    PyObject* m;

    if (PyType_Ready(&FixedWidthIndexType) < 0)
        return;

    m = Py_InitModule3("FixedWidthIndex", module_methods,
                       "FixedWidthIndex module.");

    if (m == NULL)
      return;

    Py_INCREF(&FixedWidthIndexType);
    PyModule_AddObject(m, "FixedWidthIndex", (PyObject *)&FixedWidthIndexType);
}

