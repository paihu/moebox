
function modalForm() {
    var form = document.getElementById("form");
    if (!form) {
        console.log("form not found.");
        return;
    }
    form.addEventListener("submit", function(e){
        var xhr = new XMLHttpRequest();
        if (!xhr){
            console.log("XHMLHttpRequest not found.");
            return;
        }
        var fd = new FormData(form);
        if (!fd){
            console.log("FormData create error.");
            return;
        }
        xhr.addEventListener("load", function(ev){
            document.getElementById("modal-content").innerHTML=this.responseText;
            modalForm();
        });
        xhr.open("POST",form.action);
        xhr.send(fd);
        e.preventDefault();
    });
};

window.addEventListener("load",function(){
    var ar = document.getElementsByTagName("a");
    for (var v=0;v<ar.length;v++) {
        if (ar[v].href.match(/download/)){
        ar[v].addEventListener("click",function(e){
            xhr = new XMLHttpRequest();
            if (!xhr){
            return;
            }
            xhr.open("GET",this.href,true);
            xhr.addEventListener("load",function(){
                document.getElementById("modal-content").innerHTML=this.responseText;
                document.getElementById("modal").style.display="block";
                modalForm();
            });
            xhr.send();
            e.preventDefault();
        });
    };
    };
    
    document.getElementById("modal-overlay").addEventListener("click",function(e){
        document.getElementById("modal").style.display="none";
    });
    document.getElementById("modal-overlay").addEventListener("click",function(e){
        e.stopPropagation();
    },true);
});

