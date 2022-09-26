#include <Arduino.h>
#include <MIDI.h>

struct Serial1MIDISettings : public midi::DefaultSettings
{
  static const long BaudRate = 31250;
  static const int8_t RxPin =  15;
  static const int8_t TxPin = 14;
};

MIDI_CREATE_CUSTOM_INSTANCE(HardwareSerial, Serial1, DIN_MIDI, Serial1MIDISettings);

void HandleNoteOn(byte channel, byte pitch, byte velocity) {
  Serial.println(int(pitch));

}

void HandleNoteOff(byte channel, byte pitch, byte velocity) {
  Serial.println("nada");
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9200);
  DIN_MIDI.begin(MIDI_CHANNEL_OMNI);
  DIN_MIDI.setHandleNoteOn(HandleNoteOn);
  DIN_MIDI.setHandleNoteOff(HandleNoteOff);
}

void loop() {
  // put your main code here, to run repeatedly:
  DIN_MIDI.read();
  delay(100);

}