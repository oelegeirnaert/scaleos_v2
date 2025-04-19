AI Assistant
======================================================================

Via 9090 on SRVOESTE
Podman container 

sudo podman exec -it strange_edison /bin/bash
ollama pull chevalblanc/gpt-4o-mini

to test

    ::

    curl -X POST http://srvoeste.drum-vimba.ts.net:11434/api/generate      -H "Content-Type: application/json"      -d '{
       "model": "gemma3",
       "prompt": "What is the capital of France?"
     }'



    curl -X POST http://srvoeste.drum-vimba.ts.net:11434/api/generate      -H "Content-Type: application/json"      -d '{
       "model": "chevalblanc/gpt-4o-mini",
       "prompt": "What is a musician?"
     }'