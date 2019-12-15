# Shiny App to visualize the data gathered by the Real Estate Web Crawlers

library(shiny)
library(shinydashboard)
library(shinyBS)
library(leaflet)
library(DT)
library(data.table)
library(plotly)
library(shinyWidgets)


# input data gathered by the Web Crawlers
dir <- setwd(sub(getwd(),pattern = 'dashboard',replacement = ''))
df_prices <- do.call(rbind,
                     lapply(list.files(path = 'prezzi/', pattern = '*csv', full.names = TRUE), 
                            fread))
df_prices$location <- factor(df_prices$location)
df_prices$fonte <- factor(df_prices$fonte)
df_prices <- df_prices %>% 
  mutate(prezzo_testo = prezzo,
         prezzo = gsub('€','', prezzo)) %>% 
  mutate(prezzo = gsub('.','', prezzo, fixed = TRUE)) %>% 
  mutate(prezzo = as.numeric(trimws(prezzo)))
df_prices$link <- paste0("<a href='", df_prices$link,"'target='_blank'>",df_prices$link,"</a>")
df_prices['pmq'] <- df_prices$prezzo / as.numeric(df_prices$superficie)
df_prices$data <- as.Date(df_prices$data)
df_prices <- df_prices %>% 
              select(location,
                     titolo,
                     descrizione,
                     locali,
                     prezzo,
                     superficie,
                     pmq,
                     link,
                     fonte,
                     dt=data)
df_prices.mindt <- as.Date(df_prices$dt) %>% min()
df_prices.maxdt <- as.Date(df_prices$dt) %>% max()
df_prices.dtlist <- unique(df_prices$dt) %>% unique() %>% sort()



# user interface
dashboardPage(skin = 'blue',
    dashboardHeader(title = 'Real Estate'),
    dashboardSidebar(
      sidebarMenu(id = 'tabs',
        menuItem("Cerca", tabName = "cerca"),
        menuItem("Analisi", tabName = "analisi"),
        menuItem("Grafici", tabName = "grafici"),
        menuItem('Filtri', tabName = 'filtri'),
        conditionalPanel("input.tabs=='filtri'",
                         selectInput('search_location', label = 'Location',
                                     choices = c('All',unique(as.character(df_prices$location))),
                                     multiple = TRUE, selected = 'All'),
                         selectInput('search_date', label = 'Data',
                                     choices = c('All', unique(as.character(df_prices$dt))))
        )
      )
    ),
    dashboardBody(
        tabItems(
          tabItem('cerca',
                  dataTableOutput('table_prices')
                  ),
          tabItem('analisi',
                  tabBox(width = 12,
                         tabPanel('Location',dataTableOutput('groupby_location')),
                         tabPanel('Locali', dataTableOutput('groupby_locali')))
                  ),
          tabItem('grafici',
                  tabBox(width = 12,
                         tabPanel('Superficie vs Prezzo', 
                                  plotlyOutput('chart_superficieprezzo')),
                         tabPanel('Prezzo mq', 
                                  plotlyOutput('chart_distribuzioneprezzo'),
                                  sliderTextInput('dt_chart_distribuzioneprezzo',
                                              'Data',
                                              choices = df_prices.dtlist,
                                              animate = TRUE)),
                         tabPanel('Trend pmq', 
                                  plotlyOutput('chart_trend_pmq'),
                                  sliderTextInput('dt_chart_trend_pmq',
                                                  'Data',
                                                  choices = df_prices.dtlist,
                                                  animate = TRUE)),
                         tabPanel('Boxplot', plotlyOutput('chart_pmq_boxplot')))
                  )
        )
    )
  
)




