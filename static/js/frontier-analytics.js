(function ($) {
  "use strict"; // Start of use strict

  // Toggle the side navigation
  $("#sidebarToggle, #sidebarToggleTop").on('click', function (e) {
    $("body").toggleClass("sidebar-toggled");
    $(".sidebar").toggleClass("toggled");
    if ($(".sidebar").hasClass("toggled")) {
      $('.sidebar .collapse').collapse('hide');
    };
  });


  // Close any open menu accordions when window is resized below 768px
  $(window).resize(function () {
    if ($(window).width() < 768) {
      $('.sidebar .collapse').collapse('hide');
    };
  });

  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
  $('body.fixed-nav .sidebar').on('mousewheel DOMMouseScroll wheel', function (e) {
    if ($(window).width() > 768) {
      var e0 = e.originalEvent,
        delta = e0.wheelDelta || -e0.detail;
      this.scrollTop += (delta < 0 ? 1 : -1) * 30;
      e.preventDefault();
    }
  });

  // Scroll to top button appear
  $(document).on('scroll', function () {
    var scrollDistance = $(this).scrollTop();
    if (scrollDistance > 100) {
      $('.scroll-to-top').fadeIn();
    } else {
      $('.scroll-to-top').fadeOut();
    }
  });

  // Smooth scrolling using jQuery easing
  $(document).on('click', 'a.scroll-to-top', function (e) {
    var $anchor = $(this);
    $('html, body').stop().animate({
      scrollTop: ($($anchor.attr('href')).offset().top)
    }, 1000, 'easeInOutExpo');
    e.preventDefault();
  });

})(jQuery); // End of use strict

$("#loadid").submit(function (event) {

  /* stop form from submitting normally */
  event.preventDefault();

  // add task status elements
  div = $('<div><div class="mb-1 small">Loading ES data</div><div class="progress progress-bar"></div></div><p>    </p><form class="user"><input  value="Stop Loading" class="btn btn-danger btn-user btn-block" title="stop extracting data" onclick="stopLoadingEs();"></div>');
  $('#loadFormCard').append(div);

  // create a progress bar
  var nanobar = new Nanobar({
    bg: '#0082c2',
    target: div[0].childNodes[1]
  });
  // prepare forrm data
  var dataform = $("#loadid").serialize();

  console.log(dataform);
  $.ajax({
    type: 'POST',
    url: '/loadData',
    data: dataform,
    success: function (data, status, request) {
      console.log('loadData request:', request);
      status_url = request.getResponseHeader('Location');
      status_url = status_url.split(',')[0];
      console.log('loadData result:', status_url);
      update_progress(status_url, nanobar, div[0]);
    },
    error: function () {
      console.log('Unexpected error');
    }
  });
});

function update_progress(status_url, nanobar, status_div) {
  // send GET request to status URL
  console.log('update progress url:', status_url);
  $.getJSON(status_url, function (data) {
    // update UI
    console.log(data['status']);
    percent = data['#Queries'] * 100 / data['total'];
    nanobar.go(percent);
    $(status_div.childNodes[0]).text(data['status'] + percent.toFixed(2) + '%');
    if (data['state'] == 'PROGRESS' || data['state'] == 'PENDING') {
      setTimeout(function () {
        update_progress(status_url, nanobar, status_div);
      }, 2000);
    }
    else {
      if (data['state'] == 'FAILURE') {
        alert(data['status']);
      }
      location.reload(true);

    }
  });
}


function updateClient(socket, filename) {

  /* stop form from submitting normally */
  event.preventDefault();
  // prepare forrm data
  var data = { parquetFileName: filename };
  $.ajax({
    type: 'GET',
    url: '/deleteParquet',
    data: data,
    success: function () {
      socket.emit('updateParquetDirectoryEvent');
      console.log('success')
    },
    error: function () {
      console.log('Unexpected error');
    }
  });
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function ExtractingProgress() {
  // get the last task id
  var task = getCookie('task_id');

  console.log('extracting progress for task:', task);

  // send a request to the server in order to check if the extraction task is running
  $.ajax({
    type: 'POST',
    url: '/ExtractingProgress',
    data: { 'task_id': task },
    success: function (data, status, request) {
      var task = getCookie('task_id');
      if (task != '') {
        // add task status elements
        var div = $('<div><div class="mb-1 small">Loading ES data</div><div class="progress progress-bar"></div></div><p>    </p><form class="user"><input  type="submit" value="Stop Loading" class="btn btn-danger btn-user btn-block" title="stop extracting data" onclick="stopLoadingEs();"></div>');
        $('#loadFormCard').append(div);

        // create a progress bar
        var nanobar = new Nanobar({
          bg: '#0082c2',
          target: div[0].childNodes[1]
        });

        status_url = request.getResponseHeader('Location');
        status_url = status_url.split(',')[0];
        console.log('extracting progress trying to get data from:', status_url);
        update_progress(status_url, nanobar, div[0]);
      }

    },
    error: function () {
      console.log('Unexpected error');
    }
  });

}

function stopLoadingEs() {
  // get the last task id
  var task = getCookie('task_id');

  // send a request to the server in order to check if the extraction task is running
  $.ajax({
    type: 'POST',
    url: '/stopLoadData',
    data: { 'task_id': task },
    success: function (data, status, request) {
      console.log('task stopped');
    },
    error: function () {
      console.log('Unexpected error');
    }
  });

}

function DisplayDbsOptions(select_div_id, Coolr) {
  for (dbitem in Coolr) {
    var option = $('<option value="' + dbitem + '">' + dbitem + '</option>');
    $('#' + select_div_id).append(option);

  }
}

function DisplaySchemasOptions(select_div_id, selected_db, Coolr) {
  $('#' + select_div_id).empty();
  for (item in Coolr[selected_db]) {
    var option = $('<option value="' + item + '">' + item + '</option>');
    $('#' + select_div_id).append(option);

  }
}

function DisplayNodesOptions(select_div_id, selected_db, selected_schema, Coolr) {
  $('#' + select_div_id).empty();
  var array = Coolr[selected_db][selected_schema];
  console.log(array);
  for (var i = 0; i < array.length; i++) {
    console.log(array[i]);
    var option = $('<option value="' + array[i] + '">' + array[i] + '</option>');
    $('#' + select_div_id).append(option);
  }
}


function parquetFileSelected(file) {
  event.preventDefault();
  document.getElementById("folders").style.display = "";
  file_path = file;
  document.getElementById("Filename").innerHTML = ' Folders List - ' + file_path;
}

function AddNewFolder() {

  event.preventDefault();
  // prepare forrm data
  var dataform = $("#addFolderForm").serialize();
  console.log(dataform);
  $.ajax({
    type: 'POST',
    url: '/calculateCachingEfficiency/addCachingEfficiencyFolder',
    data: dataform,
    success: function (data) {
      folders = data;
      loadFolders(folders);
      $('.selectpicker').selectpicker('refresh');


    },
    error: function () {
      console.log('Unexpected error');
    }
  });

}

function loadFolders(folders) {
  $('#selectFolder').empty();
  var length = folders.length;
  console.log(folders);
  for (var i = 0; i < length; i++) {
    var elements = folders[i];
    var option = $('<option value="' + elements + '">' + '(' + elements[0] + ' ' + elements[1] + ' ' + elements[2] + ')' + '</option>');
    $('#selectFolder').append(option);

  }

}

function calculateCachingEfficiency() {
  event.preventDefault();
  // enable stop Button
  $('#stopCalculatingCaching').prop("disabled", false);
  // prepare forrm data
  var dataform = $("#selectFolderForm").serialize();
  // extract the right values
  var formValues = dataform.split('&');
  // keep the selected folders in a list
  var folderList = [];
  for (var i = 0; i < formValues.length; i++) {
    var subStrings = formValues[i].split('=');
    folderList.push(subStrings[1])
  }
  var str = folderList.join('-');
  spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgress"></i>');
  $('#folderSection').append(spinner);
  $.ajax({
    type: 'GET',
    url: '/calculateCachingEfficiency/calculate?folders=' + str + '&parquet_file=' + file_path,
    contentType: "application/json",
    success: function (data) {
      task_id_caching = data['task_id'];
      checkCachingEfficiencyResults(task_id_caching);
    },
    error: function (e) {
      $('#spinnerProgress').remove();
      $('#stopCalculatingCaching').prop("disabled", true);
      alert(e);
    }
  });

}

function checkCachingEfficiencyResults(task_id) {
  // send a request to the server in order to check if the extraction task is running
  $.ajax({
    type: 'POST',
    url: '/calculateCachingEfficiency/calculate_status',
    data: { 'task_id': task_id },
    success: function (response) {
      var task = response['state'];
      if (task == 'SUCCESS') {
        $('#spinnerProgress').remove();
        $('#stopCalculatingCaching').prop("disabled", true);
        dataframe = response['results'];
        if (dataframe['#queries']) {
          displayResults(dataframe);
        }
        else {
          document.write(data);
        }
      }
      else {
        if (task == "FAILURE") {
          alert('task failed !!');
          $('#spinnerProgress').remove();
          $('#stopCalculatingCaching').prop("disabled", true);
        } else {
          if (task != 'REVOKED') {
            setTimeout(function () {
              checkCachingEfficiencyResults(task_id)
            }, 2000);
          }

        }
      }

    },
    error: function (e) {
      alert(e);
      $('#spinnerProgress').remove();
      $('#stopCalculatingCaching').prop("disabled", true);
    }
  });

}

function stopCalculatingCachingEfficiency(task_id_caching) {
  event.preventDefault();
  // send a request to the server in order to check if the extraction task is running
  $.ajax({
    type: 'POST',
    url: '/stopCalculating',
    data: { 'task_id': task_id_caching },
    success: function (data, status, request) {
      $('#spinnerProgress').remove();
      $('#stopCalculatingCaching').prop("disabled", true);
    },
    error: function (e) {
      alert(e);
    }
  });

}

function displayResults(data) {
  document.getElementById("Results").style.display = "";
  $('#TableBody').empty();
  if (data['folders']) {
    var rowsNumber = Object.keys(data['folders']).length;
  }
  for (var i = 0; i < rowsNumber; i++) {
    var folder = $(" <td>" + data['folders'][i] + "</td>");
    var queriesNumber = $(" <td>" + data['#queries'][i] + "</td>");
    var uniqueQueriesNumber = $(" <td>" + data['#uniqueQueries'][i] + "</td>");
    var uniquePayloadsNumber = $(" <td>" + data['#Payloads'][i] + "</td>");
    var payloadSize = $(" <td>" + data['PayloadSize (MB)'][i] + "</td>");
    var row = $('<tr></tr>');
    row.append(folder); row.append(queriesNumber); row.append(uniqueQueriesNumber); row.append(uniquePayloadsNumber); row.append(payloadSize);
    $('#TableBody').append(row);
  }

}

function save_cachingEfficiency_data(parquet_file, data) {
  if (confirm('Are you sure you want to save this caching efficiency into the ElasticSearch database?')) {
    event.preventDefault();
    spinner = $('<i class="fas fa-spinner fa-pulse" id="spinnerProgressSaving"></i>');
    $('#resultsSection').append(spinner);
    var dataform = {
      'file_name': parquet_file,
      'data': JSON.stringify(data)
    };
    console.log(dataform);
    $.ajax({
      type: 'POST',
      url: '/CachingEfficiency/storeCachingEfficiency',
      data: dataform,
      success: function (data) {
        if (data == 'success') {
          $('#spinnerProgressSaving').remove();
          alert('data saved');
        }
        else {
          document.write(data);
        }
      },
      error: function (e) {
        $('#spinnerProgressSaving').remove();
        alert(e);

      }
    });
  } else {
    // do nothings
  }


}

function removeFolderFromList(db, schema, node) {
  event.preventDefault();
  // prepare forrm data
  var dataform = { 'db': db, 'schema': schema, 'node': node };
  $.ajax({
    type: 'POST',
    url: '/calculateCachingEfficiency/removeCachingEfficiencyFolder',
    data: dataform,
    success: function (data) {
      folders = data;
      loadFolders(folders);
      $('.selectpicker').selectpicker('refresh');
    },
    error: function () {
      console.log('Unexpected error');
    }
  });
}
