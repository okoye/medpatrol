function(doc){
    if (doc.doc_type == 'Flag')
        emit(doc._id, doc)
}
