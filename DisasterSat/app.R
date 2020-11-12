#### Orginal Developer: Jordan Bales
#### Original Date: 9/1/2020
#### The purpose of this application ...

############################ Necessary Libraries ################################
library(shiny)
library(DT)
library(leaflet)
library(shinydashboard)
library(dashboardthemes)
library(shinycssloaders)
library(reticulate)
use_condaenv("DisasterSat2", required = TRUE)

############################ User Interface ################################
ui <- shinyUI(
    
    dashboardPage(
        dashboardHeader(title = "Disaster Sat Capstone"), #Open to suggestions
        dashboardSidebar(
            sidebarMenu(
                menuItem("About Us",icon = icon("user-friends"), href = "https://google.com"),
                menuItem("Source code", icon = icon("github"), href = "https://github.com/wcarruthers/xview2_uva"),
                menuItem("Dataset Information",icon = icon("paper-plane"), href = "https://openaccess.thecvf.com/content_CVPRW_2019/papers/cv4gc/Gupta_Creating_xBD_A_Dataset_for_Assessing_Building_Damage_from_Satellite_CVPRW_2019_paper.pdf"),
                menuItem("xView2 Algorithm", icon = icon("github"), href = "https://github.com/DIUx-xView/xView2_baseline"),
                menuItem("Save the Children",icon = icon("hospital"), href = "https://www.savethechildren.org/"),
                
                #Selector for Preloaded or custom
                selectInput(inputId = "customselector",
                            label = "User or Pre-Loaded Images?",
                            choices = c(Custom = "Custom", PreLoaded = "Pre-Loaded")),
                
                conditionalPanel(condition = "input.customselector == 'Custom'",

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
                
                )#Ends Conditional panel argument
            )),
        
        dashboardBody(
            shinyDashboardThemes(theme = "purple_gradient"),
            # titlePanel(h1("Infrastructure Analysis",
            #               #align = "center",
            #               style="font-family: 'Lobster',
            #                      cursive;
            #                      font-size: 16;
            #                      font-weights: 500;
            #                      line-height: 1.1;"),
            #               windowTitle = "Infrastructure Analysis"),
            
                mainPanel(
                    fluidPage(
                    fluidRow(
                        column(7, h2("Infrastructure Analysis",
                                     align = "center",
                                     style="font-family: 'Lobster',
                                 cursive;
                                 font-size: 16;
                                 font-weights: 500;
                                 line-height: 1.1;"),
                        withSpinner(imageOutput('outputImage'))
                        
                        ), 
                        column(3, offset = 2, h2("Before",
                                                 align = "center",
                                                 style="font-family: 'Lobster',
                                 cursive;
                                 font-size: 16;
                                 font-weights: 500;
                                 line-height: 1.1;"),
                        imageOutput('outputBeforeImage')
                        )),
                    fluidRow(
                        column(3,offset = 9, h2("After",
                                                align = "center",
                                                style="font-family: 'Lobster',
                                 cursive;
                                 font-size: 16;
                                 font-weights: 500;
                                 line-height: 1.1;"),
                        imageOutput('outputAfterImage'))
                    )
                        
                        #DT::dataTableOutput("TableResults", width = "100%", height = "100%")
                        
                        ) )
                
            )))
############################ Server Details ################################
server <- shinyServer(function(input,output,session) {

    
######################################### Handle Data Inputs ################################################   
    
    ##### Handle storage and use of the Before Satellite png file
    observeEvent(input$BeforeFile, {
        inFile <- input$BeforeFile
        if (is.null(inFile))
            return()
        file.copy(inFile$datapath, file.path("xview_auto/xview2/test/", inFile$name))
    })
    
    ##### Handle storage and use of the After Satellite png file
    observeEvent(input$AfterFile, {
        inFile2 <- input$AfterFile
        if (is.null(inFile2))
            return()
        file.copy(inFile2$datapath, file.path("xview_auto/xview2/test/", inFile2$name)) #This needs to be relative and overwrite
    })
    
######################################### Python Script execution  ################################################   
    
    #### Action button to run Python Script
    observeEvent(input$PythonButton,{
        req(input$BeforeFile)
        req(input$AfterFile)
        
        #Calls the Xview Python script
        source_python("xview_auto/apply_inference.py")
    })
    
    
######################################### Image Ouput Section ################################################   
    
    #### Image Output 
        #This will display the image created from apply_inference.py
    output$outputImage <- renderImage({
        
        if(input$customselector== "Custom") {
        #Requirements before predict image will be displayed
        req(input$BeforeFile)
        req(input$AfterFile)
        req(input$PythonButton)
        
        PredictionFile=list.files(path = 'xview_auto/xview2/test/',pattern='prediction.*\\.png')
        outfile <- file.path(paste('xview_auto/xview2/test/', PredictionFile,sep = "")) #input$BeforeFile$datapath
        contentType <- '.png'
        
        list(src = outfile,
             contentType=contentType,
             width = 750,
             height=750)
        {
        #No clue why this doesn't work but should make it dynamic
        #width = session$clientData$output_outputImage_width,
        #height=session$clientData$output_outputImage_height)
        }
    #}, deleteFile = FALSE) 
    } else {
        list(src = 'xview_auto/xview2/test/PreLoad_prediction.png',
             contentType='.png',
             #width = 750,
             height=function() {
                 if (session$clientData$output_outputImage_width <= 1000) {
                     (log(session$clientData$output_outputImage_width)*(1/4))
                 } else { log((session$clientData$output_outputImage_width)*(3/16) )}
             })
    }
    
}, deleteFile = FALSE) 
    
    #### Image Output for Before Image
    output$outputBeforeImage = renderImage({
        if(input$customselector== "Custom") {
        #Requirements before Before Image will be displayed
        req(input$BeforeFile)
        
        #BeforeFile=list.files(path = 'xview_auto/xview2/test/',pattern='pre_.*\\.png')
        #outfile2 <- file.path(paste('xview_auto/xview2/test/', BeforeFile,sep = "")) 
        outfile2 <- file.path("xview_auto/xview2/test/", input$BeforeFile$name)
        contentType <- '.png'
        
        list(src = outfile2,
             contentType=contentType,
             width = 350,
             height=350)
    #}, deleteFile = FALSE)
        } else {
            list(src = 'xview_auto/xview2/test/PreLoad_Before_Image.png',
                 contentType='.png',
                 #width = 350,
                 height=function() {
                     if (session$clientData$output_outputBeforeImage_width <= 1000){
                         (log( session$clientData$output_outputBeforeImage_width)*(1/4))
                     } else {log( (session$clientData$output_outputBeforeImage_width)*(3/16) )}
                 }) 
        }
    }, deleteFile = FALSE)
    
    #### Image Output for After Image
    output$outputAfterImage = renderImage({
        if(input$customselector== "Custom") {
            #Requirements before After Image will be displayed
        req(input$AfterFile)
        
        #BeforeFile=list.files(path = 'xview_auto/xview2/test/',pattern='pre_.*\\.png')
        #outfile2 <- file.path(paste('xview_auto/xview2/test/', BeforeFile,sep = "")) 
        outfile3 <- file.path("xview_auto/xview2/test/", input$AfterFile$name)
        contentType <- '.png'
        
        list(src = outfile3,
             contentType=contentType,
             width = 350,
             height=350)
    #}, deleteFile = FALSE)
        } else {
            list(src = 'xview_auto/xview2/test/PreLoad_After_Image.png',
                 contentType='.png',
                 #width = 350,
                 height=function() {
                     if (session$clientData$output_outputAfterImage_width <= 100) {
                         (log(session$clientData$output_outputAfterImage_width)*(1/4))
                     } else { log((session$clientData$output_outputAfterImagee_width)*(3/16)) }
                 }) 
        }
    }, deleteFile = FALSE)
    
# Thu Nov  5 12:24:48 2020 ----------------------------- Ask Will's opinion.
    #DataTable output
    #This will display items such as percent of damage, long, lat, etc
    # output$TableResults<- renderDataTable(input$BeforeFile,
    #                                       options = list(
    #                                           pageLength = 5)
    # )
    
    
})

shinyApp(ui = ui, server = server)
