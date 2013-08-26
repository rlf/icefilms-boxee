genre = null
category = null
worker = null

show = (show_id) ->
  current = '#' + $('.shown').attr('id')
  transitions = 
    '#main_menu' : 'hide-left',
    '#genre_menu' : if (show_id is '#movie_menu' or current is '#movie_menu') then 'hide-left' else 'hide-right',
    '#movie_menu' : 'hide-right'
  for id, t of transitions
    elem = $(id)
    if elem.hasClass('shown') or id is show_id
      cl = "shown #{t}"
      s = "Transitioning #{id} : #{elem[0].className} => "
      elem.toggleClass(cl)
      s += "#{elem[0].className}"
      console.log s
    
showGenres = (event) ->
  console.log "showGenres #{event.currentTarget}/#{event.originalEvent}"
  if event.currentTarget and event.currentTarget isnt document and event.originalEvent
    category = event.currentTarget
    $('#genre_menu').bind 'webkitTransitionEnd', (e) ->
      if e.originalEvent.propertyName is '-webkit-transform'
        active = $('article.shown > section:first-child > a')
        $.keynav.reset()
        $('#genre_menu').keynav()
        if active and active[0]
          $.keynav.setActive(active[0])
    show('#genre_menu')
  return false

addMovies = (movies) ->
  article = $('article#movie_menu')
  #section = $('<section class="muuhvie"><a href="#"><canvas width="110" height="130"/></a></section>')
  pageid = 'page' + ($('article#movie_menu > section').size() + 1)
  section = $('<section class="muuhvie" id="' + pageid + '"></section>')
  if pageid is 'page1'
    section.toggleClass('shown')
  else
    section.toggleClass('hide-bottom')
  for movie in movies
    movie.poster = 'images/empty.png' if movie.poster is 'N/A'
    console.log "poster = #{movie.poster}"
    anchor = $('<a href="#"><canvas/></a>')
    section.append(anchor)
    canvas = $('canvas', anchor)[0]
    ctx = canvas.getContext('2d')
    img = new Image()
    img.alt = movie.title
    img['data-ctx'] = ctx
    img.onload = ->
      ctx = this['data-ctx']
      #ctx.scale(110 / this.width, 200 / this.height)
      # TODO: Read the padding from the styles
      ctx.drawImage(this, 0,0)
      ctx.fillStyle = '#fff'
      ctx.lineWidth = 1
      ctx.strokeStyle = '#000'
      ctx.color = 'white'
      ctx.font = 'bold 22pt Arial'
      ctx.textAlign = 'center'
      ctx.shadowOffsetX = 2
      ctx.shadowOffsetY = 2
      ctx.shadowBlur = 3
      ctx.shadowColor = 'black'
      ctx.fillText(this.alt, 55, 110)
    img.src = movie.poster
  article.append(section)
  $('a', section).keynav('focus', 'nofocus')
  
onMovieData = (e) ->
  console.log "E: #{e}/#{category.id}/#{getGenre()}"
  data = e.data
  if data.success
    console.log "Got something... #{data.message}"
    addMovies(data.data.movies)
  else
    console.log "Finished"
    event = {}
    event.currentTarget = category
    showGenres(event)
    
getGenre = ->
  return $('canvas', genre).attr('data-alt').toLowerCase()
  
showMovies = ->
  if event.currentTarget and event.currentTarget isnt document and category
    genre = event.currentTarget
    show('#movie_menu')
    $('#movie_menu').html('') # Clean...
    $.keynav.reset()
    # TODO: do the ajax-thingy for fetching movies (in a worker please)
    if worker
      worker.terminate()
    d = new Date()
    worker = new Worker('js/icerss_worker.js?_=' + d.valueOf())
    worker.addEventListener('message', onMovieData)
    t = category.id
    g = getGenre()
    worker.postMessage("#{t}/popular/#{g}")
  return false
  
showMain = (event) ->
  if event.currentTarget isnt document
    show('#main_menu')
    genre = null
    $.keynav.reset()
    $('#main_menu').keynav()
    if category then $.keynav.setActive(category)
    return false
  
# TODO: Move styling into the style-sheet (somehow)
paintMainImageWithCaption = (jqimg, width=1175, textoffset=140) ->
  img = jqimg[0]
  alt = img.alt
  w = jqimg.width() # image dimensions
  h = jqimg.height()
  height = h
  x = textoffset
  y = h - h/4
  canvas = $("<canvas width='#{width}' height='#{height}'/>")
  canvas['data-alt'] = alt
  ctx = canvas[0].getContext('2d')
  newImage = new Image()
  newImage.onload = ->
    ctx.drawImage(newImage, 0, 0, w, h)
    ctx.fillStyle = '#fff'
    ctx.lineWidth = 1
    ctx.strokeStyle = '#000'
    ctx.color = 'white'
    ctx.font = 'bold 48pt Arial'
    ctx.textAlign = 'left'
    ctx.shadowOffsetX = 2
    ctx.shadowOffsetY = 2
    ctx.shadowBlur = 3
    ctx.shadowColor = 'black'
    ctx.fillText(alt, x, y)
  newImage.src = img.src
  jqimg.replaceWith(canvas)    
  
paintGenreImageWithCaption = (jqimg, width=300, height=200) ->
  img = jqimg[0]
  w = jqimg.width() # image dimensions
  h = jqimg.height()
  x = w/2
  y = height - height/6
  #console.log "x,y = #{x},#{y} #{w}x#{h}, img=#{img}"
  canvas = $("<canvas width='#{width}' height='#{height}'/>")
  $(canvas).attr('data-alt', img.alt)
  ctx = canvas[0].getContext('2d')
  
  newImage = new Image()
  newImage.alt = img.alt
  newImage.onload = ->
    ctx.drawImage(this, 0,0, w,h)
    ctx.fillStyle = '#fff'
    ctx.lineWidth = 1
    ctx.strokeStyle = '#000'
    ctx.color = 'white'
    ctx.font = 'bold 28pt Arial'
    ctx.textAlign = 'center'
    ctx.shadowOffsetX = 2
    ctx.shadowOffsetY = 2
    ctx.shadowBlur = 3
    ctx.shadowColor = 'black'
    ctx.fillText(this.alt, x, y)
  newImage.src = img.src
  jqimg.replaceWith(canvas)    
  
goBack = (e) ->
  if e.which is 37
    if genre then showGenres(e) else showMain(e)
    return false
  return true

goNext = (e) ->
  if e.which is 39
    if not genre then showGenres(e)
    return false
  return true
  
escAction = (e) ->
  if e.which is 27
    shown = $('.shown').attr('id')
    if shown is 'movie_menu' 
      showGenres(e)
    else if shown is 'genre_menu' 
      showMain(e)
      
jQuery ->
  # Main Menu
  $('#main_menu > section > a#movies').click(showGenres)
  $('#main_menu > section > a#tv').click(showGenres)
  $('#main_menu > section > a#movies').bind('keydown', (e) -> if e.which is 39 then showGenres(e))
  $('#main_menu > section > a#tv').bind('keydown', (e) -> if e.which is 39 then showGenres(e))
  $('#main_menu > section > a > img').each ->
    img = $(this)
    this.onload = ->
      paintMainImageWithCaption(img)
  # Genre Menu
  $('#genre_menu > section > a').click(showMovies)
  $('#genre_menu > section > a > img').each ->
    img = $(this)
    this.onload = ->
      paintGenreImageWithCaption(img)
  $('#genre_menu a.back').bind('keydown', goBack)
  # Movie Menu
  $('section#main_menu > a').keynav('focus', 'nofocus')
  # Focus changes on anchors change class on the parent (section) - NOT on movies
  $('a').bind 'focus', -> $(this).parent().addClass 'focus'
  $('a').bind 'blur', -> $(this).parent().removeClass 'focus'  
  $.rule('article').append('-webkit-transition: all 2s ease-in-out;')
  $(window).keydown(escAction)
  $.keynav.setActive($('article > section:first-child > a')[0])
