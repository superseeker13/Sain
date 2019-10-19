-- Launch from command line with fceux -lua listener.lua

require "builtins.scripts.socket"
local socket = require("socket")

-- load namespace
local socket = require("socket")

-- create a TCP socket and bind it to the local host, at py client
local server = assert(socket.bind("*", 0))

-- select port 
local ip, port = server:getsockname()

-- print a message informing what's up
print("Connected on port " .. port)

--Start emulators
emu.speedmode("normal")
while true do

    -- wait for a connection from any client
    local client = server:accept()
    -- make sure we don't block waiting for this client's line
    client:settimeout(10)
    -- receive the line
    local line, err = client:receive()
    -- if there was no error, send response

    -- Execute instructions from packet

    client:close()

    --Debugging
    --emu.message("Still running")
    emu.frameadvance() -- This essentially tells FCEUX to keep running
end

-- Needs ran after each nn attempt
-- emu.softreset()

-- Need function to reset
-- table joypad.read(int player)

-- Write directy to memory
-- joypad.set(int player, table input)
-- joypad.write(int player, table input)


-- May need to use if evNet becomes bulky
-- emu.exec_count(int count, function func)

-- Idea record movie of best/worst attempts
-- Stretch goal: csv dump to graph using matplotlib
-- Stretch goal: GUI Library couuld be used to display
-- nn on screen. --Note may need on sepreate thread of some sort.
