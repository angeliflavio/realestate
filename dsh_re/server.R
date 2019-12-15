# Shiny App to visualize the data gathered by the Real Estate Web Crawlers

library(shiny)
library(dplyr)
library(leaflet)
library(sp)
library(leaflet)
library(data.table)
library(plotly)
library(ggplot2)
library(stringr)
  

# input data gathered by the Web Crawlers
dir <- setwd(sub(getwd(),pattern = 'dashboard',replacement = ''))
df_prices <- do.call(rbind,
                     lapply(list.files(path = 'prezzi/', pattern = '*csv', full.names = TRUE), 
                            function(x)fread(x, dec = ',')))
df_prices$location <- factor(df_prices$location)
df_prices$fonte <- factor(df_prices$fonte)
df_prices <- df_prices %>% 
              mutate(prezzo_testo = prezzo,
                     prezzo = gsub('€','', prezzo)) %>% 
              mutate(prezzo = gsub('.','', prezzo, fixed = TRUE)) %>% 
              mutate(prezzo = as.numeric(trimws(prezzo)))
df_prices$link <- paste0("<a href='", df_prices$link,"'target='_blank'>",df_prices$link,"</a>")
df_prices['pmq'] <- round(df_prices$prezzo / as.numeric(df_prices$superficie))
df_prices$data <- as.Date(df_prices$data)
df_prices$locali <- str_extract(df_prices$locali, '\\d+') %>% as.numeric()
df_prices$superficie <- as.numeric(gsub('.','',df_prices$superficie,fixed = TRUE))
df_prices <- df_prices %>% 
              select(location,
                     titolo,
                     descrizione,
                     locali,
                     prezzo,
                     superficie,
                     pmq,
                     link,
                     #fonte,
                     dt=data)


# Define server logic 
shinyServer(function(input,output){
  
  output$table_prices <- renderDataTable({
    if (input$search_location=='All') {df_prices} else 
      df_prices <- df_prices %>% 
                    filter(location==input$search_location)
    if (input$search_date=='All') {df_prices} else 
      df_prices <- df_prices %>% 
        filter(dt==as.Date(input$search_date))
    df_prices <- df_prices %>% 
                  filter(pmq < 20000)
    datatable(df_prices,
              extensions = c('Buttons'),
              options = list(
                dom = 'Bfrtip',
                buttons = c('excel', 'copy'),
                scrollX = TRUE,
                #truncate cell content for column 'description'
                columnDefs = list(list(
                  targets = 2,
                  render = JS(
                    "function(data, type, row, meta) {",
                    "return type === 'display' && data != null && data.length > 30 ?",
                    "'<span title=\"' + data + '\">' + data.substr(0, 30) + '...</span>' : data;",
                    "}")
                ))
              ),
              class = 'display',
              filter = 'top', rownames = FALSE, escape = FALSE)
  })
  
  
  
  output$groupby_location <- renderDataTable({
    if (input$search_date=='All') {df_prices} else 
      df_prices <- df_prices %>% 
        filter(dt==as.Date(input$search_date))
    df_prices <- df_prices %>% 
      filter(pmq < 20000)
    
    df_prices %>% 
      group_by(location) %>% 
      summarise(PrezzoMedio = round(mean(prezzo, na.rm = TRUE)),
                nr = n(),
                PrezzoMediano = round(median(prezzo, na.rm = TRUE)),
                pmqMedio = round(mean(pmq, na.rm = TRUE)),
                pmqMediano = round(median(pmq, na.rm = TRUE)),
                na = sum(is.na(prezzo))) %>% 
      datatable(options = list(scrollX=TRUE))
  })
  
  
  
  output$groupby_locali <- renderDataTable({
    if (input$search_location=='All') {df_prices} else 
      df_prices <- df_prices %>% 
        filter(location==input$search_location)
    if (input$search_date=='All') {df_prices} else 
      df_prices <- df_prices %>% 
        filter(dt==as.Date(input$search_date))
    df_prices <- df_prices %>% 
      filter(pmq < 20000)
    
    df_prices %>% 
      group_by(locali) %>% 
      summarise(PrezzoMedio = round(mean(prezzo, na.rm = TRUE)),
                nr = n(),
                PrezzoMediano = round(median(prezzo, na.rm = TRUE)),
                pmqMedio = round(mean(pmq, na.rm = TRUE)),
                pmqMediano = round(median(pmq, na.rm = TRUE)),
                na = sum(is.na(prezzo)))%>% 
      datatable(options = list(scrollX=TRUE))
  })
  
  
  
  output$chart_superficieprezzo <- renderPlotly({
    if (input$search_location=='All') {df_prices} else 
      df_prices <- df_prices %>% 
        filter(location==input$search_location)
    if (input$search_date=='All') {df_prices} else 
      df_prices <- df_prices %>% 
        filter(dt==as.Date(input$search_date))
    df_prices <- df_prices %>% 
      filter(pmq < 20000)
    
    df_prices %>% 
      plot_ly(x=~superficie, y=~prezzo, 
              color=~location, frame=~df_prices$dt,
              type = 'scatter', mode = 'markers', alpha = 0.3) %>% 
      animation_slider() %>% 
      animation_opts(transition = 0, redraw = FALSE)
  })
  
  
  output$chart_distribuzioneprezzo <- renderPlotly({
    if (input$search_location=='All') {df_prices} else 
      df_prices <- df_prices %>% 
        filter(location==input$search_location)
    # if (input$search_date=='All') {df_prices} else 
    #   df_prices <- df_prices %>% 
    #     filter(dt==as.Date(input$search_date))
    df_prices <- df_prices %>% 
      filter(dt==as.Date(input$dt_chart_distribuzioneprezzo))
    df_prices <- df_prices %>% 
      filter(pmq < 20000)
    
    text.position <- cut(df_prices$pmq, breaks = seq(0,10000,250)) %>% 
      table() %>% 
      data.frame() %>% 
      top_n(1,Freq) %>% 
      select(Freq) %>% 
      as.numeric()
    c2 <- ggplot(df_prices, aes(pmq, fill = location)) + 
      geom_histogram(color = 'white', position = 'identity', alpha = 0.4,
                     breaks = seq(0,10000,250)) +
      geom_vline(aes(xintercept = mean(pmq)), color='red') + 
      geom_vline(aes(xintercept = median(pmq)), color='red', linetype = 'dashed') +
      scale_x_continuous(breaks = seq(0,8000,1000), limits = c(0,10000)) +
      # annotate(geom = 'text', x=mean(df_prices$pmq)*1.6, y=0.8*text.position,
      #          label=paste('media',round(mean(df_prices$pmq))), color='red') +
      ylab('Nr annunci') +
      theme(panel.background = element_rect(fill = 'white'))
    ggplotly(c2)
  })
  
  
  output$chart_trend_pmq <- renderPlotly({
    if (input$search_location=='All') {df_prices} else 
      df_prices <- df_prices %>% 
        filter(location==input$search_location) 
    df_prices <- df_prices %>% 
      filter(pmq < 20000) %>% 
      filter(dt <= input$dt_chart_trend_pmq)
    
    c <- df_prices %>% 
      group_by(dt, location) %>%
      summarise(pmq = mean(pmq, na.rm = TRUE)) %>%
      ggplot(aes(dt, pmq, colour=location)) +
      geom_line() + geom_point() +
      theme(panel.background = element_rect(fill = 'white'))
    ggplotly(c)
  })
  
  
  output$chart_pmq_boxplot <- renderPlotly({
    if (input$search_location=='All') {df_prices} else 
      df_prices <- df_prices %>% 
        filter(location==input$search_location) 
    df_prices <- df_prices %>% 
      filter(pmq < 20000)
    
    c <- df_prices %>%
      filter(pmq < 20000) %>%
      ggplot(aes(x=as.factor(dt),y=pmq)) +
      geom_boxplot(fill = 'gray', color='navyblue') + 
      xlab('') + 
      scale_y_continuous(breaks = seq(0,max(df_prices$pmq,na.rm = TRUE),2000)) +
      theme(panel.background = element_rect(fill = 'white'))
    ggplotly(c)
  })
  

})




  