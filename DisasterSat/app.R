#### Orginal Developer: Jordan Bales
#### Original Date: 9/1/2020
#### The purpose of this application ...

############################ Necessary Libraries ################################
library(shiny)
library(DT)
library(leaflet)
library(shinydashboard)
library(reticulate)

############################ Load in ancillary items ################################


############################ User Interface ################################
ui <- shinyUI(
    
    dashboardPage(
        dashboardHeader(title = "Disaster Sat Capstone"), #Open to suggestions
        dashboardSidebar(
            sidebarMenu(
                menuItem("About Us", href = "https://google.com"),
                menuItem("Source code", icon = icon("github"), href = "https://github.com/wcarruthers/xview2_uva"),
                menuItem("Dataset Information", href = "https://openaccess.thecvf.com/content_CVPRW_2019/papers/cv4gc/Gupta_Creating_xBD_A_Dataset_for_Assessing_Building_Damage_from_Satellite_CVPRW_2019_paper.pdf")
            )),
        dashboardBody(
            titlePanel("Infrastructure Analysis"),
            
            sidebarLayout(
                sidebarPanel(width = 2, 
                             
                             #file input for Befor Image
                             fileInput(inputId = 'BeforeFile',
                                       label ="Please upload your before image",
                                       accept = c('.png'),
                                       multiple = FALSE),
                             
                             #file input for After Image
                             fileInput(inputId = 'AfterFile',
                                       label ="Please upload your before image",
                                       accept = c('.png'), 
                                       multiple = FALSE),
                             
                             #Action button to run Python script.
                             actionButton("PythonButton", "Analyze")
                ),
                mainPanel(
                    fluidRow(
                        column(width = 12, height=100), 
                        imageOutput('outputImage'),
                        DT::dataTableOutput("TableResults", width = "100%", height = "100%")))
                
            ))))

############################ Server Details ################################
server <- shinyServer(function(input,output,session) {
    
    #setwd("~/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/test/") #This will need to be replaced with a relative path to test/

    ##### Handle storage and use of the Before Satellite png file
    observeEvent(input$BeforeFile, {
        inFile <- input$BeforeFile
        if (is.null(inFile))
            return()
        file.copy(inFile$datapath, file.path("~/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/test/", inFile$name)) #This needs to be relative and overwrite
    })
    
    ##### Handle storage and use of the After Satellite png file
    observeEvent(input$AfterFile, {
        inFile2 <- input$AfterFile
        if (is.null(inFile2))
            return()
        file.copy(inFile2$datapath, file.path("~/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/test/", inFile2$name)) #This needs to be relative and overwrite
    })
    
    
    #### Action button to run Python Script
    #This will take some testing, but something similar to this will do it 
    #https://stackoverflow.com/questions/49344520/running-codes-upon-clicking-on-action-button-in-r-shiny
    
    observeEvent(input$PythonButton,{
        req(input$BeforeFile)
        req(input$AfterFile)
        source_python("~/Desktop/GIT_Repos/xview2_uva/xview_auto/apply_inference.py")
    })
    
    #Image Output 
        #This will display the image created from apply_inference.py
        #Will change soon
    output$outputImage <- renderImage({
        #Requirements before predict image will be displayed
        req(input$BeforeFile)
        req(input$AfterFile)
        req(input$PythonButton)
        
        PredictionFile=list.files(path = '~/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/test/',pattern='prediction.*\\.png')
        outfile <- file.path(paste('~/Desktop/GIT_Repos/xview2_uva/xview_auto/xview2/test/', PredictionFile,sep = "")) #input$BeforeFile$datapath
        contentType <- '.png'
        list(src = outfile,
             contentType=contentType,
             width = 800,
             height=800)
    }, deleteFile = FALSE)
    
# Thu Nov  5 12:24:48 2020 ----------------------------- Ask Will's opinion.
    #DataTable output
        #This will display items such as percent of damage, long, lat, etc
    # output$TableResults<- renderDataTable(mtcars,
    #                                       options = list(
    #                                           pageLength = 5)
    # )
    
    
})

shinyApp(ui = ui, server = server)
