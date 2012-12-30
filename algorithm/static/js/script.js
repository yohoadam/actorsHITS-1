/* Script for CSCE 470 search engine
 *
 */
window.onload=setupFunc
var actor_template = _.template($('#actor_template').html(),null,{variable:'t'});
var result_template = _.template($('#result_template').html());
var alert_template = _.template($('#alert_template').html());

$('#actorsearch form').submit(function(ev) {
    var q = $(this).find('input[name=query]').val();
    ajax_search(q);
    return false;
});


function ajax_search(q) {
  $.ajax('/search',{
      data:{q:q},
      timeout:150000,
      success: function(data) {
        var result_div = $('#actorsearch .results');
        result_div.empty();
        result_div.show();
        result_div.append($(result_template(data)));
        var actor_divs = _.map(data.actors, actor_template);
        result_div.append(actor_divs.join(''));
      },
      error: function(jqXHR,textStatus,errorThrown) {
        var error;
        if(textStatus=='error') {
          if(jqXHR.status==0)
            error = "Could not connect to server. Try running ./serve.py.";
          else
            error = jqXHR.status+" : "+errorThrown;
        } else {
          error = textStatus;
        }

        var alert = alert_template({error:error});
        $('#actorsearch form').after(alert);
        $('#actorsearch .results').hide();
      },
      dataType: 'json',
  });
}


function handleSubmit(dropdown){
    //alert("submit pressed"+dropdown.value);
    $('#actorsearch .results').hide();
    ajax_search(dropdown.value);
}

function getGenres(q){
  $.ajax('/genres',{
      data:{q:q},
      timeout:15000,
      success: function(data) {
        //alert('successfull'+data);
        fillGenres(data);
      },
      error: function (jqXHR,textStatus,errorThrown){
        alert('error '+textStatus);
      },
      dataType:'text',
  });
}

function setupFunc() {
    //alert("ajax page loaded");
    getGenres('Comedy');
}

function fillGenres(data){
    var list = document.getElementById("genres_drop");

    var val = data.split("|");
    /*
    happen to add an extra | at the end
    also have to retain 'Select Genre'
    */
    list.length=val.length;
    for (i=0;i<val.length-1;i++){
        list[i+1].text=val[i];
        list[i+1].value=val[i];
    }
}
