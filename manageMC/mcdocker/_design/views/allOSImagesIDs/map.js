function(doc)
{
    if (doc.doc_type == 'DockerImage')
    {
        emit([doc.imageType,doc.parent,doc.imageID], null);
    }
}