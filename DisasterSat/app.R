#### Orginal Developer: Jordan Bales
#### Original Date: 9/1/2020
#### The purpose of this application ...

############################ Necessary Libraries ################################
library(shiny)
library(DT)
library(leaflet)
library(shinydashboard)

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
                                       accept = c('.jpg','.jpeg')),
                             
                             #file input for After Image
                             fileInput(inputId = 'AfterFile',
                                       label ="Please upload your before image",
                                       accept = c('.jpg','.jpeg')),
                             
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
    
    #This will take some testing, but something similar to this will do it 
        #https://stackoverflow.com/questions/49344520/running-codes-upon-clicking-on-action-button-in-r-shiny
    #observeEvent(input$PythonButton,{
        #source("apply_finference.py")
    #})
    
    #Handle the image file
    observeEvent(input$BeforeFile, {
        inFile <- input$BeforeFile
        if (is.null(inFile))
            return()
        #file.copy(inFile$datapath, file.path("c:/temp", inFile$name) ) #Need to figure out path 
    })
    
    #Image Output 
        #This will display the image created from apply_inference.py
    output$outputImage <- renderImage({
        req(input$BeforeFile)
        
        outfile <- input$BeforeFile$datapath
        contentType <- input$BeforeFile$type
        list(src = outfile,
             contentType=contentType,
             width = 400,
             height=400)
    }, deleteFile = TRUE)
    
    
    #DataTable output
        #This will display items such as percent of damage, long, lat, etc
    output$TableResults<- renderDataTable(mtcars,
                                          options = list(
                                              pageLength = 5)
    )
    
    
})

shinyApp(ui = ui, server = server)
