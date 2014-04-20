function(doc)
{
    if (doc.doc_type == 'MinecraftServer')
    {
        emit([doc.binary,doc._id,doc.name], null);
    }
}