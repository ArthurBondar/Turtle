<?php

/*
    System Info
    Return format: [dataTime, CPULoad, MemTotal, MemFree]
    JSON format
*/
echo json_encode( array(
    'datetime' => getDateTime(),
    'load' => getServerLoad(),
    'mem' => getServerMem()
));

# Get Linux server load and convert
# Based on number of cores, return in percentage
function getServerLoad()
{
    $loads=sys_getloadavg();
    $core_nums=trim(shell_exec("grep -P '^physical id' /proc/cpuinfo | wc -l"));
    $load= ($loads[0]/$core_nums) * 100;
    if($load > 100) $load = 100;
    return $load;
}


# Get Linux server RAM usage
# Based on $free -m command
# Return [ TotalMem, FreeMem ]
function getServerMem()
{
    if(file_exists('/proc/meminfo'))  {
        $data = explode("\n", file_get_contents("/proc/meminfo"), 4);
        for ($i = 0; $i < 3; $i++) {
            $meminfo[$i] = preg_replace("/[^0-9?![:space:]]/", "", $data[$i]);
            $meminfo[$i] = intval( $meminfo[$i] / 1024 );
        }
        /*
        # Getting Total RAM Memory
        $meminfo[0] = preg_replace("/[^0-9?![:space:]]/", "", $data[0]);
        $meminfo[0] = intval( $meminfo[0] / 1024 );
        # Getting Free RAM Memory
        $meminfo[1] = preg_replace("/[^0-9?![:space:]]/", "", $data[2]);
        $meminfo[1] = intval( $meminfo[1] / 1024 );
        */
        return $meminfo;
    }
    else
        return false;
}


# Get Datetime from the server
function getDateTime()
{
    date_default_timezone_set('Canada/Halifax');
    $date = date('d/m/Y H:i', time());
    return $date;
}


?>