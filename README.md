2071 Milestone and Project
Milestone --> https://docs.google.com/document/d/1OcTnsw8ynj8Lw2W4IkcMDlVWKreWBgQ5qaIviF7XthI/edit?tab=t.0 

Project --> https://docs.google.com/document/d/14-HsNPGXvYbsxszqTRLJgNjl2ebnvuqzkZIjxmfJO8k/edit?tab=t.0

Milestone:
Basic Requirements
1. Your token ring network must contain at least N - 1 STM32s (where N is the number of members in your team, adjusted for any team members who are absent).
2. Your token ring network must send a single byte as the ‘token’. It does not matter what this byte is for the pass level.
3. The ‘head’ STM can be any device in the chain and designated by your team.
4. After receiving the token, the STM should hold it for 250ms before passing it on to the next device in the chain.
5. Each STM32 should use its onboard green LED to indicate when it has possession of the token.
6. Communication should begin when the ‘head’ STM sends the first packet that is triggered by receiving an arbitrary message from a PC over UART.
7. Whenever the ‘head’ STM receives the token (indicating an entire loop), it should send it over UART to the PC to be displayed on any console [e.g. Arduino serial, puTTy, or a Python handler] and then pass it on to the next device.

Stream Requirements
1. Your token ring network must contain N STM32s (where N is the number of members in your team).
2. Instead of an arbitrary byte, the ‘head’ STM must receive a message from a Python script as the initial message. 
3. Each device must append its ID [defined previously] to the received string before passing it on.
4. When the ‘head’ STM receives the final message, it will still send it to the PC to be displayed and not start the message over again until the Python script requests it to do so.

Full Requirements
1. A ‘checksum’ must be introduced to the communication system between each STM to ensure the data is not being corrupted.  
    - The checksum is calculated by performing a bitwise XOR between each byte in the received string (excluding the previous checksum). For example, if the string has 4 bytes, the final result would be ((B0 ^ B1) ^ B2) ^ B3).
    - Once calculated, the STM should verify the calculated checksum matches the received checksum. If it does not, the STM should halt the ring and leave its LED on.
    - After appending its name to the original message, the STM must now re-calculate the checksum and append it to the end of the message before sending it on.
2. The ‘head’ STM must be dynamic and will be chosen at random by your manager during your demonstration.
    - This means every STM must be capable of acting as the ‘head’ without reprogramming
