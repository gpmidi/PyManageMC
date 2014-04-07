function(doc)
{
    if (doc.doc_type == 'MinecraftServerBinary')
    {
        emit([doc.typeName,doc.releaseStatus,doc.version], null);
    }
}