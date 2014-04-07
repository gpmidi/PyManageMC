function(doc)
{
    if (doc.doc_type == 'MinecraftServerBinary')
    {
        emit([doc.releaseStatus,doc.typeName,doc.version], null);
    }
}