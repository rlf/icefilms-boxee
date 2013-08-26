(function() {
  var addMovies, category, escAction, genre, getGenre, goBack, goNext, onMovieData, paintGenreImageWithCaption, paintMainImageWithCaption, show, showGenres, showMain, showMovies, worker;
  genre = null;
  category = null;
  worker = null;
  show = function(show_id) {
    var cl, current, elem, id, s, t, transitions, _results;
    current = '#' + $('.shown').attr('id');
    transitions = {
      '#main_menu': 'hide-left',
      '#genre_menu': show_id === '#movie_menu' || current === '#movie_menu' ? 'hide-left' : 'hide-right',
      '#movie_menu': 'hide-right'
    };
    _results = [];
    for (id in transitions) {
      t = transitions[id];
      elem = $(id);
      _results.push(elem.hasClass('shown') || id === show_id ? (cl = "shown " + t, s = "Transitioning " + id + " : " + elem[0].className + " => ", elem.toggleClass(cl), s += "" + elem[0].className, console.log(s)) : void 0);
    }
    return _results;
  };
  showGenres = function(event) {
    console.log("showGenres " + event.currentTarget + "/" + event.originalEvent);
    if (event.currentTarget && event.currentTarget !== document && event.originalEvent) {
      category = event.currentTarget;
      $('#genre_menu').bind('webkitTransitionEnd', function(e) {
        var active;
        if (e.originalEvent.propertyName === '-webkit-transform') {
          active = $('article.shown > section:first-child > a');
          $.keynav.reset();
          $('#genre_menu').keynav();
          if (active && active[0]) {
            return $.keynav.setActive(active[0]);
          }
        }
      });
      show('#genre_menu');
    }
    return false;
  };
  addMovies = function(movies) {
    var anchor, article, canvas, ctx, img, movie, pageid, section, _i, _len;
    article = $('article#movie_menu');
    pageid = 'page' + ($('article#movie_menu > section').size() + 1);
    section = $('<section class="muuhvie" id="' + pageid + '"></section>');
    if (pageid === 'page1') {
      section.toggleClass('shown');
    } else {
      section.toggleClass('hide-bottom');
    }
    for (_i = 0, _len = movies.length; _i < _len; _i++) {
      movie = movies[_i];
      if (movie.poster === 'N/A') {
        movie.poster = 'images/empty.png';
      }
      console.log("poster = " + movie.poster);
      anchor = $('<a href="#"><canvas/></a>');
      section.append(anchor);
      canvas = $('canvas', anchor)[0];
      ctx = canvas.getContext('2d');
      img = new Image();
      img.alt = movie.title;
      img['data-ctx'] = ctx;
      img.onload = function() {
        ctx = this['data-ctx'];
        ctx.drawImage(this, 0, 0);
        ctx.fillStyle = '#fff';
        ctx.lineWidth = 1;
        ctx.strokeStyle = '#000';
        ctx.color = 'white';
        ctx.font = 'bold 22pt Arial';
        ctx.textAlign = 'center';
        ctx.shadowOffsetX = 2;
        ctx.shadowOffsetY = 2;
        ctx.shadowBlur = 3;
        ctx.shadowColor = 'black';
        return ctx.fillText(this.alt, 55, 110);
      };
      img.src = movie.poster;
    }
    article.append(section);
    return $('a', section).keynav('focus', 'nofocus');
  };
  onMovieData = function(e) {
    var data, event;
    console.log("E: " + e + "/" + category.id + "/" + (getGenre()));
    data = e.data;
    if (data.success) {
      console.log("Got something... " + data.message);
      return addMovies(data.data.movies);
    } else {
      console.log("Finished");
      event = {};
      event.currentTarget = category;
      return showGenres(event);
    }
  };
  getGenre = function() {
    return $('canvas', genre).attr('data-alt').toLowerCase();
  };
  showMovies = function() {
    var d, g, t;
    if (event.currentTarget && event.currentTarget !== document && category) {
      genre = event.currentTarget;
      show('#movie_menu');
      $('#movie_menu').html('');
      $.keynav.reset();
      if (worker) {
        worker.terminate();
      }
      d = new Date();
      worker = new Worker('js/icerss_worker.js?_=' + d.valueOf());
      worker.addEventListener('message', onMovieData);
      t = category.id;
      g = getGenre();
      worker.postMessage("" + t + "/popular/" + g);
    }
    return false;
  };
  showMain = function(event) {
    if (event.currentTarget !== document) {
      show('#main_menu');
      genre = null;
      $.keynav.reset();
      $('#main_menu').keynav();
      if (category) {
        $.keynav.setActive(category);
      }
      return false;
    }
  };
  paintMainImageWithCaption = function(jqimg, width, textoffset) {
    var alt, canvas, ctx, h, height, img, newImage, w, x, y;
    if (width == null) {
      width = 1175;
    }
    if (textoffset == null) {
      textoffset = 140;
    }
    img = jqimg[0];
    alt = img.alt;
    w = jqimg.width();
    h = jqimg.height();
    height = h;
    x = textoffset;
    y = h - h / 4;
    canvas = $("<canvas width='" + width + "' height='" + height + "'/>");
    canvas['data-alt'] = alt;
    ctx = canvas[0].getContext('2d');
    newImage = new Image();
    newImage.onload = function() {
      ctx.drawImage(newImage, 0, 0, w, h);
      ctx.fillStyle = '#fff';
      ctx.lineWidth = 1;
      ctx.strokeStyle = '#000';
      ctx.color = 'white';
      ctx.font = 'bold 48pt Arial';
      ctx.textAlign = 'left';
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;
      ctx.shadowBlur = 3;
      ctx.shadowColor = 'black';
      return ctx.fillText(alt, x, y);
    };
    newImage.src = img.src;
    return jqimg.replaceWith(canvas);
  };
  paintGenreImageWithCaption = function(jqimg, width, height) {
    var canvas, ctx, h, img, newImage, w, x, y;
    if (width == null) {
      width = 300;
    }
    if (height == null) {
      height = 200;
    }
    img = jqimg[0];
    w = jqimg.width();
    h = jqimg.height();
    x = w / 2;
    y = height - height / 6;
    canvas = $("<canvas width='" + width + "' height='" + height + "'/>");
    $(canvas).attr('data-alt', img.alt);
    ctx = canvas[0].getContext('2d');
    newImage = new Image();
    newImage.alt = img.alt;
    newImage.onload = function() {
      ctx.drawImage(this, 0, 0, w, h);
      ctx.fillStyle = '#fff';
      ctx.lineWidth = 1;
      ctx.strokeStyle = '#000';
      ctx.color = 'white';
      ctx.font = 'bold 28pt Arial';
      ctx.textAlign = 'center';
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;
      ctx.shadowBlur = 3;
      ctx.shadowColor = 'black';
      return ctx.fillText(this.alt, x, y);
    };
    newImage.src = img.src;
    return jqimg.replaceWith(canvas);
  };
  goBack = function(e) {
    if (e.which === 37) {
      if (genre) {
        showGenres(e);
      } else {
        showMain(e);
      }
      return false;
    }
    return true;
  };
  goNext = function(e) {
    if (e.which === 39) {
      if (!genre) {
        showGenres(e);
      }
      return false;
    }
    return true;
  };
  escAction = function(e) {
    var shown;
    if (e.which === 27) {
      shown = $('.shown').attr('id');
      if (shown === 'movie_menu') {
        return showGenres(e);
      } else if (shown === 'genre_menu') {
        return showMain(e);
      }
    }
  };
  jQuery(function() {
    $('#main_menu > section > a#movies').click(showGenres);
    $('#main_menu > section > a#tv').click(showGenres);
    $('#main_menu > section > a#movies').bind('keydown', function(e) {
      if (e.which === 39) {
        return showGenres(e);
      }
    });
    $('#main_menu > section > a#tv').bind('keydown', function(e) {
      if (e.which === 39) {
        return showGenres(e);
      }
    });
    $('#main_menu > section > a > img').each(function() {
      var img;
      img = $(this);
      return this.onload = function() {
        return paintMainImageWithCaption(img);
      };
    });
    $('#genre_menu > section > a').click(showMovies);
    $('#genre_menu > section > a > img').each(function() {
      var img;
      img = $(this);
      return this.onload = function() {
        return paintGenreImageWithCaption(img);
      };
    });
    $('#genre_menu a.back').bind('keydown', goBack);
    $('section#main_menu > a').keynav('focus', 'nofocus');
    $('a').bind('focus', function() {
      return $(this).parent().addClass('focus');
    });
    $('a').bind('blur', function() {
      return $(this).parent().removeClass('focus');
    });
    $.rule('article').append('-webkit-transition: all 2s ease-in-out;');
    $(window).keydown(escAction);
    return $.keynav.setActive($('article > section:first-child > a')[0]);
  });
}).call(this);
