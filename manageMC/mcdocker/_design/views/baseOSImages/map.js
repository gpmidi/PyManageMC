function(doc)
{
    if (doc.doc_type == 'DockerImage' && doc.imageType == 'BaseImage')
    {
        emit([doc.parent,doc.imageID], doc);
    }
}