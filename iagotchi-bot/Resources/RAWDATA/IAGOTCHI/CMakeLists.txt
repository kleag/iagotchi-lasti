configure_file(introductions.top introductions.top @ONLY)

install(FILES 
  simplecontrol.top
  ${CMAKE_CURRENT_BINARY_DIR}/introductions.top
  iagotchi_concepts.top
  relance.top
  questionphilosophique.top
  DESTINATION ${ChatScriptInstallDir}/RAWDATA/IAGOTCHI
)

