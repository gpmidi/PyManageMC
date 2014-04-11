function(doc)
{
    if (doc.doc_type == 'DockerImage' && doc.imageType == 'UserImage')
    {
        emit([doc.parent,doc.imageID], doc);
    }
}