document.addEventListener('click', hideAutocomplete);
const input = document.querySelector('input');
const a = document.querySelector('a');
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("qtm-tab");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" qtm-active", "");
    }

    document.getElementById(tabName).style.display = "block";
//    debugger;
//    if(tabName=='tab2'){
//        dateForProductTabCtrl = document.getElementById('dateForProductTab');
//        productNameCtrl = document.getElementById('productName');
//        showSelectedOption(dateForProductTabCtrl, 'productName', 'plot_graphPrdName', productNameCtrl.value);
//    }else if(tabName=='tab3'){
//        customerNameCtrl = document.getElementById('customerName');
//        dateForCustomerTabCtrl = document.getElementById('dateForCustomerTab');
//        showSelectedOption(dateForCustomerTabCtrl, 'customerName', 'plot_graphCustomerName', customerNameCtrl.value);
//    }
    evt.currentTarget.className += " qtm-active";
}
function hideAutocomplete(){
const dropdown = document.getElementById('suggestionsProductName');
const dropdown2 = document.getElementById('suggestionsCustomerName');
 // Hide list when user clicks outside of input or list
  document.addEventListener('click', function(event) {
      if (event.target !== input && event.target !== a) {
        dropdown.style.display = 'none';
        dropdown2.style.display = 'none';
      }
  });
 }
function getSuggestions(searchCtrl, listName, urlValue){
 const dropdown = document.getElementById(listName);
 dropdown.innerHTML = "";
 // If search term is empty, hide list and return
 dropdown.style.display = 'none';
 if (!searchCtrl.value) {
   dropdown.style.display = 'none';
   return;
 }

 $.ajax({
    type: 'GET',
    url: '/'+urlValue,
    contentType: 'application/json',
    data: {'search': encodeURIComponent(searchCtrl.value.trim())},
    success: function(responseData) {
          const dropdown = document.getElementById(listName);
          dropdown.innerHTML = "";
          if (responseData.length === 0) {
             dropdown.style.display = 'none';
             return;
          }
           // Add options to list
          responseData.forEach(option => {
            var link = document.createElement("a");
            link.innerHTML = option;
            dropdown.appendChild(link);
          });

          // Show list
          dropdown.style.display = 'block';

          // Add an event listener to the dropdown menu to handle the user's selection
          dropdown.addEventListener("click", function(event) {
            // Get the selected item
            var selected = event.target.innerHTML;
            // Update the input element with the selected item
            searchCtrl.value = selected;
            if(listName.indexOf('Product')>0){
                dateForProductTabCtrl = document.getElementById('dateForProductTab');
                showSelectedOption(dateForProductTabCtrl, 'productName', 'plot_graphPrdName', selected)
            }else{
                dateForCustomerTabCtrl = document.getElementById('dateForCustomerTab');
                showSelectedOption(dateForCustomerTabCtrl, 'customerName', 'plot_graphCustomerName', selected)
            }

            // Hide the dropdown menu
            dropdown.style.display = "none";
          });
        }
    });
}

function showSelectedOption(selectCtrl, fieldName, identifierName, autoCompleteValue){
  selectedOption = selectCtrl.value;
  field=document.getElementById(fieldName);
  if(autoCompleteValue!=null){
        field.value=autoCompleteValue;
  }
  if(document.getElementById(identifierName)!=null){
     document.getElementById(identifierName).style.display="none";
  }
  document.getElementById("loaderPrd").style.display = "block";
  document.getElementById("loaderCstmr").style.display = "block";
  if(field!=null){
      $.ajax({
        type: 'GET',
        url: '/usageComparison',
        contentType: 'application/json',
        data: {'date': encodeURIComponent(selectCtrl.value.trim()), [fieldName]:field.value},
        success: function(responseData) {
        document.getElementById("loaderPrd").style.display = "none";
        document.getElementById("loaderCstmr").style.display = "none";
        document.getElementById(identifierName).style.display="block";
        if(document.getElementById(identifierName)!=null){
            document.getElementById(identifierName).innerHTML='';
            document.getElementById(identifierName).innerHTML=responseData.html;
            if(document.getElementById(identifierName+"Json")!=null){
                control=document.getElementById(identifierName+"Json");
                if(identifierName=='plot_graphCustomerName' && document.getElementById("plot_graph1")!=null && document.getElementById("plot_graph1")!= ''){
                    fig_json=document.getElementById("plot_graph1").innerHTML;
                    document.getElementById("plot_graph1").innerHTML='';
                    if(fig_json != ''){
                        Plotly.newPlot('plot_graph1', JSON.parse(fig_json));
                    }
                }else{
                    fig_json=document.getElementById("plot_graph2").innerHTML;
                    document.getElementById("plot_graph2").innerHTML='';
                    if(fig_json != ''){
                        Plotly.newPlot('plot_graph2', JSON.parse(fig_json));
                    }

                }

            }
        }
        }
      });
  }
}