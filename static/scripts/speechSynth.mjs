export default class SpeechSynth{
    static populateVoiceList() {
        var synth = window.speechSynthesis;
        var inputForm = document.querySelector('form');        
        var voiceSelect = document.querySelector('select');
        var voices = [];
        voices = synth.getVoices();
        for(var i = 0; i < voices.length ; i++) {
            var option = document.createElement('option');
            option.textContent = voices[i].name + ' (' + voices[i].lang + ')';
            if(voices[i].default) {
                option.textContent += ' -- DEFAULT';
            }
            option.setAttribute('data-lang', voices[i].lang);
            option.setAttribute('data-name', voices[i].name);
            voiceSelect.appendChild(option);
        }
    };
    static speak(what){
        var synth = window.speechSynthesis;
        var voiceSelect = document.querySelector('select');
        var utterThis = new SpeechSynthesisUtterance(what);
        let voices = synth.getVoices();
        var selectedOption = voiceSelect.selectedOptions[0].getAttribute('data-name');
        for(var i = 0; i < voices.length ; i++) {
            if(voices[i].name === selectedOption) {
            utterThis.voice = voices[i];
            }
        }
        synth.speak(utterThis);
    };
};