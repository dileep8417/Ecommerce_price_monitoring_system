$("document").ready(()=>{
    $(".submit").click(()=>{
        $(".loader").css("display","block")
    });
    var uid = $("#userid").attr("data-id"); 
    console.log("monitor");

    $("#monitoring-items").empty();

    function loadMonitor(){
        $("#monitoring-items").empty();
        $.ajax({
            "url":"/monitor?uid="+uid,
            "method":'GET',
             success:function(resp){
                 console.log(resp)
                 let items = resp
                 if(items.length==0){
                     $("#monitoring-items").append("<h5 class='text-blue text-lighten-2'>No products are monitoring</h5>").html();
                 }else{
                    $("#monitoring-items").append("<h5 class='text-blue text-lighten-2'>Monitoring Products</h5>").html();
                 }
                 for(i=0;i<items.length;i++){
                        $("#monitoring-items").append(`<div class="col s12 m6">
                        <div class="p-content">
                            <div class="card">
                                <p class="site-name">${items[i].site}</p>
                                <div class=""><h6 class="p-name">${items[i].title}</h6></div>
                                <div class="card-content">
                                    <table class="table">
                                        <tr>
                                            <th>Actual Price:</th>
                                            <td class="actual-price">₹${items[i].actual}</td>
                                        </tr>
                                        <tr>
                                            <th>Current Price:</th>
                                            <td class="current-price">₹${items[i].current}</td>
                                        </tr>
                                        <tr>
                                            <td><p class="del removeItem" data-id="${items[i].id}"><i data-id="${items[i].id}" class="removeItem material-icons">delete</i></p></td>
                                            <td><a href="${items[i].url}" target="_blank" class="visit"><i class="material-icons">open_in_new</i></a></td>
                                        </tr>
                                    </table> 
                                </div>
                            </div>
                        </div>
                    </div>`);
                }
                 $(".loader").css("display","none");
             }
        });
    }

    function addToMonitor(site,userid,title,price,url){
        $.ajax({
            url:`./addToMonitor?userid=${userid}&url=${url}&price=${price}&title=${title}&site=${site}`,
            method:"GET",
            success:function(resp){
                $(".added").remove();
                loadMonitor();
                $(".loader").css("display","none");
            }
        }).fail(()=>{
            $(".loader").css("display","none");
        });
    }

    $(".monitor-btn").click(function(e){
        $(".loader").css("display","block");
        let site = $(this).attr("data-site");
        let url = $(this).attr("data-url");
        let price = $(this).attr("data-price");
        let userid = $(this).attr("data-id");
        let title = $(this).attr("data-title");
        $(".monitor-btn").removeClass("added");
        $(this).addClass("added");
        addToMonitor(site,userid,title,price,url);
     });

     loadMonitor();
     $(".removeItem").unbind('click');
     $("#monitoring-items").on("click",".removeItem",function(e){
        e.stopImmediatePropagation();
       if(confirm("Do you want to remove monitoring?")){
        $(".loader").css("display","block");
        let id = $(this).attr("data-id");
        $.ajax({
            url:`/remove?id=${id}`,
            method:"GET",
            success:function(resp){
                loadMonitor();
                $(".loader").css("display","none");
            }
        }).fail(()=>{
           $(".loader").css("display","none");
        });
       }
})
});