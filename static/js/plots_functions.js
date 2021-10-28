$( document ).ready(function() {



    // Add Listeners Group
    var Plot_countQueries_perDBs = document.getElementById('COOLDBs');
    if (Plot_countQueries_perDBs) {
      Plot_countQueries_perDBs.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_countQueries_perDBs.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_countQueries_NotCachedPerType = document.getElementById('NotCachedQueriesPerType');
    if (Plot_countQueries_NotCachedPerType) {
      Plot_countQueries_NotCachedPerType.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_countQueries_NotCachedPerType.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_countQueries_perSchema = document.getElementById('queriesPerSchema');
    if (Plot_countQueries_perSchema){
      Plot_countQueries_perSchema.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_countQueries_perSchema.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_percQueries_perSchema = document.getElementById('queriesPercentagePerSchema');
    if (Plot_percQueries_perSchema) {
      Plot_percQueries_perSchema.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_percQueries_perSchema.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_percQueries_perNode = document.getElementById('queriesPercentagePerNode');
    if (Plot_percQueries_perNode) {
      Plot_percQueries_perNode.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_percQueries_perNode.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_non_payloads = document.getElementById('non_payload_queries');
    if (Plot_non_payloads) {
      Plot_non_payloads.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_non_payloads.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_non_payloads_node = document.getElementById('non_payload_queries_node');
    if (Plot_non_payloads_node) {
      Plot_non_payloads_node.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_non_payloads_node.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_timeDistribution = document.getElementById('timedistr');
    if (Plot_timeDistribution) {
      Plot_timeDistribution.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_timeDistribution.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_QueryTime = document.getElementById('queriesQueryTime');
    if (Plot_QueryTime) {
      Plot_QueryTime.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_QueryTime.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_DbTime = document.getElementById('queriesDBtime');
    if (Plot_DbTime) {
      Plot_DbTime.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_DbTime.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_sizeDist = document.getElementById('sizeDistr');
    if (Plot_sizeDist) {
      Plot_sizeDist.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_sizeDist.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_sizePercentagePerSchema = document.getElementById('sizePercentageSchema');
    if (Plot_sizePercentagePerSchema) {
      Plot_sizePercentagePerSchema.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_sizePercentagePerSchema.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_sizePercentagePerNode = document.getElementById('sizePercentageNode');
    if (Plot_sizePercentagePerNode) {
      Plot_sizePercentagePerNode.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_sizePercentagePerNode.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_HighQueryTime_Schema = document.getElementById('highQueryTimeSchema');
    if (Plot_HighQueryTime_Schema) {
      Plot_HighQueryTime_Schema.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_HighQueryTime_Schema.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }

    var Plot_HighQueryTime_Node = document.getElementById('highQueryTimeNode');
    if (Plot_HighQueryTime_Node ) {
      Plot_HighQueryTime_Node.addEventListener( 'changePlot' , changePlotEventHandler , false);
      Plot_HighQueryTime_Node.addEventListener( 'changeScale' , changeScaleEventHandler , false);
    }



    var time_tab = document.getElementById('Timedistribution');
    if (time_tab) {
      time_tab.addEventListener( 'autosize' , resizePlotHandler , false);
    }
    var  size_tab = document.getElementById('Sizedistribution');
    if (size_tab) {
      size_tab.addEventListener( 'autosize' , resizePlotHandler , false);
    }
    var highQuery_tab = document.getElementById('Highquerytime');
    if (highQuery_tab) {
      highQuery_tab.addEventListener( 'autosize' , resizePlotHandler , false);
    }


});



// create events
function ChangePlotType(graphDiv, selectID ) {
     var elem = document.getElementById(graphDiv);
     var event = new CustomEvent('changePlot', { detail: {
       select: selectID,
       div: graphDiv}
     });
     // Dispatch the event
    elem.dispatchEvent(event);
}

function ChangeLogScale(graphDiv, selectID, logID) {
    var elem = document.getElementById(graphDiv);
    var event = new CustomEvent('changeScale', { detail: {
        select: selectID,
        log: logID,
        div: graphDiv
      }});
    // Dispatch the event
   elem.dispatchEvent(event);
}
function AutoSizePlot(tab, tab_divs){
  var elem = document.getElementById(tab);
   var event = new CustomEvent('autosize', { detail: {divs: tab_divs }});
   elem.dispatchEvent(event);
}


// event functions

function resizePlotHandler(e){
  setTimeout(
  function(){
      console.log('enter');
      var tab_divs = e.detail.divs;
      var plots_Length = tab_divs.length;
      for (var i = 0; i < plots_Length; i++) {
          var div = tab_divs[i];
          var graph = document.getElementById(div);
          Plotly.relayout(graph, {autosize: true});
      }
   }, 300);


}

function changePlotEventHandler(e){
        //  get the select option
        var sel = document.getElementById(e.detail.select);
        var graphID = document.getElementById(e.detail.div);
        // split the plot type from its mode
        var sel_values = sel.value.split(" ");
        var sel_plot = sel_values[0];
        var sel_mode = sel_values[1];
        // update in the plot
        if (sel_plot == 'scatter') {
          var update = {
              type: sel_plot,
              mode: sel_mode,
              hoverinfo: 'all',
          };
        } else {
          if (sel_plot == 'bar'){
            var update = {
                type: sel_plot,
                barmode: sel_mode,
                hoverinfo: 'all',
            };
          } else {
            var update = {
                type: sel_plot,
                textinfo: 'none'
            };
          }
        }

        Plotly.restyle(graphID, update);
}
function changeScaleEventHandler(e){
        //  get elements by ID
        var sel = document.getElementById(e.detail.select);
        var log = document.getElementById(e.detail.log);
        var graph = document.getElementById(e.detail.div);
        // split the plot type from its mode
        var sel_values = sel.value.split(" ");
        var sel_plot = sel_values[0];
        var sel_mode = sel_values[1];
        // get the log checkbox value
        var log_value = log.checked;
        if ( sel_plot != 'pie'){
          // update the plot
          if (log.checked) {
             var update = {
               'yaxis.type' : "log",

             }
          } else {
            var update = {
              'yaxis.type' : "",

            }
          }

          Plotly.relayout(graph, update);
        } else {
           log.checked = false;
        }

}

// Get Plot Data Functions

function getCoolDbsCount( user ,  task ) {
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressCOOLDBs"></i>');
  $('#COOLDBs').append(spinner);
  var data = { 'userID' : user , 'task' : task};
  $.ajax({
      type: 'POST',
      url: '/Plots/countPerDb',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_countQueries_perDBs').checked;
          var sel = document.getElementById('select_countQueries_perDBs').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawPlotWithMultipleTraces('COOLDBs', 'count of queries per db instances', 'dbs', 'count of queries',plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });

}
function getCountNotCachedPerTypeForDb(user ,db, task) {
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressNotCachedQueriesPerType"></i>');
  $('#NotCachedQueriesPerType').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/countNotCachedForDb',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_countQueries_pertype').checked;
          var sel = document.getElementById('select_countQueries_pertype').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawPlotWithMultipleTraces('NotCachedQueriesPerType', 'count of not cached queries per type for a given DB', 'db', 'count of not cached queries',plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });

}
function getCountQueriesPerSchema(user, db, task) {
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressqueriesPerSchema"></i>');
  $('#queriesPerSchema').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/countQueriesPerSchema',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_countQueries_perSchema').checked;
          var sel = document.getElementById('select_countQueries_perSchema').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawSimplePlot('queriesPerSchema', 'count of queries per Schema for a given DB', 'schemas', 'count of queries',plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}
function getQueryPercPerSchema(user,db,task){
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressqueriesPercentagePerSchema"></i>');
  $('#queriesPercentagePerSchema').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/queryPercentagePerSchema',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_Percentage_Schema').checked;
          var sel = document.getElementById('select_queryPercentage_perSchema').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawPlotWithMultipleTraces('queriesPercentagePerSchema', ' query percentage per Schema for a given DB', 'schemas', '%', plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function getQueryPercPerNode(user,db,schema,task){
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressqueriesPercentagePerNode"></i>');
  $('#queriesPercentagePerNode').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db, 'schema': schema};
  $.ajax({
      type: 'POST',
      url: '/Plots/queryPercentagePerNode',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_Percentage_Schema_Node').checked;
          var sel = document.getElementById('select_queryPercentage_perNode_forschema').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawPlotWithMultipleTraces('queriesPercentagePerNode', ' query percentage per Node for a given DB/schema', 'nodes', '%', plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function getNonPayloadQuerySchema(user,db,task) {
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressnon_payload_queries"></i>');
  $('#non_payload_queries').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/countNonPayloadPerSchema',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_non_payload').checked;
          var sel = document.getElementById('select_non_payload').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawPlotWithMultipleTraces('non_payload_queries', 'Count of non-payload queries per schema', 'schemas', 'count', plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function getNonPayloadQueryNode(user,db,schema,task) {
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressnon_payload_queries_node"></i>');
  $('#non_payload_queries_node').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db, 'schema': schema};
  console.log(data);
  $.ajax({
      type: 'POST',
      url: '/Plots/countNonPayloadPerNode',
      data: data,
      success: function(data) {
        console.log(data);
          var log = document.getElementById('log_non_payload_node').checked;
          var sel = document.getElementById('select_non_payload_node').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawPlotWithMultipleTraces('non_payload_queries_node', ' Count of non-payload queries per node for a given db/schema ', 'nodes', 'count', plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function getTimeDistribution(user, db, task) {
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgresstimedistr"></i>');
  $('#timedistr').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/TimeDistribution',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_timeDist').checked;
          var sel = document.getElementById('select_timeDist').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawPlotWithMultipleTraces('timedistr', 'time distribution of queries', 'time', 'count of queries' ,plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });


}

function getQueryTime(user, db , task){
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressqueriesQueryTime"></i>');
  $('#queriesQueryTime').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/countQueriesPerQueryTime',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_timeDist').checked;
          var sel = document.getElementById('select_querytime').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawPlotWithMultipleTraces('queriesQueryTime', 'count of queries per QueryTime', 'QueryTime (ms)', 'count of queries' ,plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function getDbTime(user, db , task) {
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressqueriesDBtime"></i>');
  $('#queriesDBtime').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/countQueriesPerDbTime',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_dbTime').checked;
          var sel = document.getElementById('select_dbTime').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawPlotWithMultipleTraces('queriesDBtime', 'count of queries per DbTime', 'DB time (ms)', 'count of queries' ,plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function getSizeDistribution(user, db, task) {
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgresssizeDistr"></i>');
  $('#sizeDistr').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/responseSizeDistribution',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_sizeDist').checked;
          var sel = document.getElementById('select_sizeDist').value;
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
            mode = plot[1];
          }
          drawSimplePlot('sizeDistr', 'response size distribution', 'time', 'response size (KB)' ,plot_type, data, barmode, mode,log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function getSizeDistPerSchema(user, db, task){
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgresssizePercentageSchema"></i>');
  $('#sizePercentageSchema').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/sizePercentagePerSchema',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_Percentage_Size').checked;
          var sel = document.getElementById('size_Percentage').value;
          console.log(sel);
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
              mode = plot[1];
          }
          drawSimplePlot('sizePercentageSchema', 'response size percentage per schema', 'schema', 'response size %' ,plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function getSizeDistPerNode(user, db,schema ,task){
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgresssizePercentageNode"></i>');
  $('#sizePercentageNode').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db, 'schema': schema};
  $.ajax({
      type: 'POST',
      url: '/Plots/sizePercentagePerNode',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_Percentage_Size_Node').checked;
          var sel = document.getElementById('size_PercentageNode').value;
          console.log(sel);
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
              mode = plot[1];
          }
          drawSimplePlot('sizePercentageNode', 'response size percentage per node for a given db/schema', 'nodes', 'response size %' ,plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function getHighQueryPerSchema(user,db, task) {
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgresshighQueryTimeSchema"></i>');
  $('#highQueryTimeSchema').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db};
  $.ajax({
      type: 'POST',
      url: '/Plots/HighQueryDistPerSchema',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_HighQuery_Schema').checked;
          var sel = document.getElementById('select_HighQuery_schema').value;
          console.log(sel);
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
              mode = plot[1];
          }
          drawPlotWithMultipleTraces('highQueryTimeSchema', 'High Quey Time distribution per Schema', 'time', 'count of high query times' ,plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });
}

function  getHighQueryPerNode(user,db,schema, task){
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgresshighQueryTimeNode"></i>');
  $('#highQueryTimeNode').append(spinner);
  var data = { 'userID' : user , 'task' : task, 'db': db, 'schema': schema};
  $.ajax({
      type: 'POST',
      url: '/Plots/HighQueryDistPerNode',
      data: data,
      success: function(data) {
          var log = document.getElementById('log_HighQuery_Node').checked;
          var sel = document.getElementById('select_HighQuery_Node').value;
          console.log(sel);
          var plot = sel.split(' ');
          var plot_type = plot[0];
          var barmode = null;
          var mode = null;
          if (plot_type == 'bar'){
            barmode = plot[1];
          } else {
              mode = plot[1];
          }
          drawPlotWithMultipleTraces('highQueryTimeNode', 'High Quey Time distribution per Node for a given Schema', 'time', 'count of high query times' ,plot_type, data, barmode, mode, log);
      },
      error: function() {
          console.log('Unexpected error');
      }
  });

}


function drawSimplePlot(div, title, xtitle, ytitle, plot_type, data, barmode, scattermode, log){
          var plot_data = [];
          var keys = Object.keys(data);
          if (plot_type == 'pie'){
            var trace = {
                labels: data[keys[1]],
                values: data[keys[0]],
                type: plot_type,
                name: '',
            };
            if (plot_type == 'pie'){
              trace.hoverinfo= 'label+percent+name';
              trace.textinfo= 'none';
            }
            var layout = {
              title: title,
              autosize: true
            }
          } else {
              var trace = {
                  x: data[keys[1]],
                  y: data[keys[0]],
                  type: plot_type
              };
              var layout = {
                title: title,
                xaxis: {
                   title: xtitle,
                   automargin: true,
                 },
                 yaxis: {
                   title: ytitle,
                   automargin: true,
                 },
                 autosize: true

              };
              if (scattermode){
                trace.mode = scattermode;
              } else {
                if (barmode) {
                  layout.barmode= barmode;
                }
              }
              if (log) {
                layout.yaxis.type = "log";
                layout.yaxis.autorange = true;
              };

          }


          plot_data.push(trace);
          // delete the spinner
          var spinner = '#spinnerProgress' + div;
          console.log(spinner);
          $(spinner).remove();
          Plotly.newPlot(div, plot_data, layout, {responsive: true});
}

function drawPlotWithMultipleTraces(div, title, xtitle, ytitle, plot_type, data, barmode, scattermode, log) {
          var traces = []
          for(var key in data) {
              var value  = data[key];
              var axis_keys =  Object.keys(value);
              var trace = {
                  x: value[axis_keys[1]],
                  y: value[axis_keys[0]],
                  name: key ,
                  hoverinfo : key ,
                  type: plot_type
              };
              if (scattermode){
                trace.mode = scattermode;
              }
              traces.push(trace);
          };
          var layout = {
            title: title,
            hoverlabel: { namelength: "40" },
            xaxis: {
               title: xtitle,
               //automargin: true,
             },
             yaxis: {
               title: ytitle,
               //automargin: true,
             },
          };
          if ( div == 'queriesPercentagePerNode' ) {
            layout.autosize = true;
          }
          if (log == true) {
            layout.yaxis.type = "log";
            layout.yaxis.autorange = true;
          };
          if (barmode) {
            layout.barmode= barmode;
          };
          var spinner = '#spinnerProgress' + div;
          console.log(spinner);
          $(spinner).remove();
          Plotly.newPlot(div, traces, layout, {responsive:true});

}
