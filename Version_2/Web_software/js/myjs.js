


// Attaches AJAX function when document is loaded
$(document).ready( function() {
    
    // Fetches data from the server every interval
    setInterval(getServerStat, 5000);
    // Enabling popovers on buttons
    $('[data-toggle="popover"]').popover();
    $('.popover-dismiss').popover({
        trigger: 'focus'
    });
    $('#datetimepicker3').datetimepicker({
        format: 'LT'
    });

});



// Highlight the menu buttons - Active
$(function() {
    // this will get the full URL at the address bar
    var url = window.location.href;

    // passes on every "a" tag
    $(".navbar a").each(function() {
        // checks if its the same on the address bar
        if (url == (this.href)) {
            $(this).closest("li").addClass("active");
            //for making parent of submenu active
           $(this).closest("li").parent().parent().addClass("active");
        }
    });
}); 


// AJAX function to get Time, CPU and Mem
function getServerStat() {
    $.ajax({ 
        url: "/php/sysinfo.php", 
        success: function(response) {
            var res = JSON.parse(response);
            //console.log(res);
            res.load = parseInt(res.load);
            // Updating datetime
            $("#status-datetime").html(res.datetime);
            // Updating text above bars
            $("#status-cpu").html("Load: " + res.load + "%");
            $("#status-mem").html("Memory: " + (res.mem[0]-res.mem[1]) + "MB");
            // Converting to percentage
            var mem = parseInt( ((res.mem[0]-res.mem[1])/res.mem[0])*100 ) ;
            // Updating the bar graphs
            $('#status-bar-cpu').css( {'width' : res.load + "%"} );
            $('#status-bar-mem').css( {'width' : mem + "%"} );
            // Changing bar graph colors
            // CPU bar
            if(res.load < 33) {
                $('#status-bar-cpu').removeClass("bg-success bg-warning bg-danger");
                $('#status-bar-cpu').addClass("bg-success");
            } else if(res.load < 66) {
                $('#status-bar-cpu').removeClass("bg-success bg-warning bg-danger");
                $('#status-bar-cpu').addClass("bg-warning");
            } else {
                $('#status-bar-cpu').removeClass("bg-success bg-warning bg-danger");
                $('#status-bar-cpu').addClass("bg-danger");
            }
            // Mem Bar
            if(mem < 33) {
                $('#status-bar-mem').removeClass("bg-success bg-warning bg-danger");
                $('#status-bar-mem').addClass("bg-success");
            } else if(mem < 66) {
                $('#status-bar-mem').removeClass("bg-success bg-warning bg-danger");
                $('#status-bar-mem').addClass("bg-warning");
            } else {
                $('#status-bar-mem').removeClass("bg-success bg-warning bg-danger");
                $('#status-bar-mem').addClass("bg-danger");
            }
        
        }
    });
}