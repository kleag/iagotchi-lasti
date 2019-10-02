project(IAGOTCHI NONE)

cmake_minimum_required(VERSION 2.8)

message("ENV{CHATSCRIPTINSTALLDIR} $ENV{IAGOTCHICHATSCRIPTINSTALLDIR}")
set(ChatScriptInstallDir $ENV{IAGOTCHICHATSCRIPTINSTALLDIR})
# 
# message("ENV{LIMA_PACKRUN} $ENV{LIMA_PACKRUN}")
# set(LIMA_PACKRUN $ENV{LIMA_PACKRUN})


if (UNIX)
  set(CHATSCRIPT_BIN "./LinuxChatScript64")
  set(TAGGER_BIN "tree-tagger-french")
else()
  set(CHATSCRIPT_BIN "chatscript.exe")
  set(TAGGER_BIN "tag-french.bat")
endif()



add_subdirectory(Resources)


install(DIRECTORY libs DESTINATION ${CMAKE_INSTALL_PREFIX})
install(DIRECTORY db DESTINATION ${CMAKE_INSTALL_PREFIX})
install(DIRECTORY data DESTINATION ${CMAKE_INSTALL_PREFIX})
install(DIRECTORY generator DESTINATION ${CMAKE_INSTALL_PREFIX})
install(DIRECTORY text_generator DESTINATION ${CMAKE_INSTALL_PREFIX})


configure_file(chatscript_settings.py chatscript_settings.py @ONLY)
configure_file(lima.py lima.py @ONLY)
configure_file(chatscript_externals.py chatscript_externals.py @ONLY)
configure_file(rule_generator.py rule_generator.py @ONLY)
configure_file(synthese.py synthese.py @ONLY)
configure_file(chrono.py chrono.py @ONLY)
configure_file(main.py main.py @ONLY)
configure_file(test_chatscript.py test_chatscript.py @ONLY)
# configure_file(automatons/config.json automatons/config.json @ONLY)

install(
  FILES
      ${CMAKE_CURRENT_BINARY_DIR}/main.py
      test_synthese.py
      chatscript.py
      ${CMAKE_CURRENT_BINARY_DIR}/chatscript_externals.py
      ${CMAKE_CURRENT_BINARY_DIR}/chatscript_settings.py
      ${CMAKE_CURRENT_BINARY_DIR}/rule_generator.py
      ${CMAKE_CURRENT_BINARY_DIR}/synthese.py
      ${CMAKE_CURRENT_BINARY_DIR}/test_chatscript.py
      bottle.py
      osc.py
      ${CMAKE_CURRENT_BINARY_DIR}/chrono.py
      ${CMAKE_CURRENT_BINARY_DIR}/lima.py
      log.py
      wiki_text_nlp.py
      index.html
      preprocessing.py
      similarity.py
      similarity_test.txt
      test_generator.py
      model.py
      data.py
      test_lima.py
      entrypoint-iagotchi.sh
      botresponse.py
      test_database.py
      test_dumpjson.py
      iagotchiGUI.py
      get_sentences_from_rules.py
  DESTINATION ${CMAKE_INSTALL_PREFIX}
  
)
