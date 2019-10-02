configure_file(introductions.top introductions.top @ONLY)

install(FILES 
  simplecontrol.top
  ${CMAKE_CURRENT_BINARY_DIR}/introductions.top
  iagotchi_concepts.top
  g5.top
  g5_questions.top
  g5_subtopic3.top
  g5_subtopic2.top
  g5_subtopic1.top
  relance.top
  questionphilosophique.top
  articles.top
  DESTINATION ${ChatScriptInstallDir}/RAWDATA/IAGOTCHIG5
)

