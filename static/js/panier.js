var productBtns = document.getElementsByClassName('update-panier');

for (var i = 0; i < productBtns.length; i++){

    productBtns[i].addEventListener('click', function(){

        var productId = this.dataset.product;

        var action = this.dataset.action;

        if (user === "AnonymousUser"){
            addCookieArticle(productId, action);
        }else{
            updateUserCommande(productId, action);
        }
    })

}


function addCookieArticle(productId, action){
    console.log("l'utilisateur n'est pas authentifie");

    if(action == "add"){
        if(panier[productId] == undefined){
            panier[productId] = {"qte":1};
        }else{
            panier[productId]["qte"] += 1;
        }
    }

    if(action == "remove"){
        panier[productId]["qte"] -= 1;
        if( panier[productId]["qte"] <= 0){
            delete panier[productId];
        }
    }


    document.cookie = "panier=" + JSON.stringify(panier) + ";domain=;path=/";

    console.log(panier);
    location.reload();
}

function updateUserCommande(productId, action){

    var url = '/update_article/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({"product_id": productId, "action": action})
    })

    .then((response) => {
        return response.json();
    })

    .then((data) => {
        console.log('data', data);
        location.reload();
    })
}