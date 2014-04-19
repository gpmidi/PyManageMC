
function setupLogViewer(
            serverId,idNum,
            defaultEnable,
            startOffset,ioType,
            freq,chunk,maxRows
            ) {
    idNum = idNum || 0;
    defaultEnable = defaultEnable || true;
    startOffset = startOffset || 0;
    ioType = ioType || "stdout";
    freq = freq || 1000;
    chunk = chunk || 1024*256;
    maxRows = maxRows || 5000;

    var isPartial=false;
    var currentOffset=startOffset;
    var lastLine=NaN;
    var logViewerLoc="#logViewerLoc"+idNum;
    var logViewer="#logViewer"+idNum;
    var logViewerLoadLine="#logViewerLoadLine"+idNum;
    var logViewerLoad="#logViewerLoad"+idNum;
    var logViewerPartialLine="#logViewerPartialLine"+idNum;

    function scrollViewerEnd() {
        var height = $(logViewerLoc).get(0).scrollHeight;
        $(logViewerLoc).animate({
            scrollTop: height
        }, 500);
    }

    function doLogViewerUpdate() {
        // Limits
        // TODO: Delete many at once to improve performance
        while ($(logViewer+" > div").length > maxRows) {
            $(logViewer).find('div').first().remove();
        }

        function handleRow(line,isFullLine) {
            isFullLine = isFullLine || true;

            if (isPartial) {
                // Have a partial row in last element
                line = $(logViewerPartialLine).text() + line;
                $(logViewerPartialLine).remove();
                isPartial=false;
            }

            if (isFullLine) {
                $("<div />").text(line).appendTo(logViewer);
            } else {
                $("<div />").text(line).addClass('partialLogLine')
                    .attr("id",logViewerPartialLine).appendTo(logViewer);
            }
        }

        function haveLogViewerUpdate(data) {
            if (data.success) {
                currentOffset=data.newOffset;

                data.lines.map(handleRow);
                if (data.partial) {
                    isPartial = true;
                    handleRow(data.partial,false);
                }

                scrollViewerEnd();

                if (data.hasOverflow) {
                // There is more so lets call it now
                    Dajaxice.mclogs.fetchLogSegment(haveLogViewerUpdate,
                        serverId, chunk, currentOffset,
                        true, ioType
                        );
                }
            } else {
                // TODO: Display error message
                scrollViewerEnd();
            }
        }

        Dajaxice.mclogs.fetchLogSegment(haveLogViewerUpdate,
            serverId, chunk, offset=currentOffset,
            tail=true, ioType=ioType
            );
    }

    function enableLogLoading() {
        $(logViewerLoc).css({
            height: "500px",
            width: "500px"
        });
        $(logViewerLoadLine).remove();
        setInterval(doLogViewerUpdate, freq);
    }

    // Init
    if (defaultEnable) {
        // Enable updates
        enableLogLoading();
    } else {
        // Disable updates
        $(logViewerLoad).click(function(e) {
            e.preventDefault();
            scrollViewerEnd();
            enableLogLoading();
        });
    }

}


