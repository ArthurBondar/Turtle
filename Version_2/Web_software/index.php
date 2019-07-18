<?php
  require "header.php";
?>

<main role="main" class="col-md-12 ml-sm-auto col-lg-12 px-4">


    <!--
        System Time [dd/mm/yyyy hh:mm]
    -->
    <h2 class="col-md-12 col-sm-12 col-lg-12" id="status-datetime">Waiting...</h2>
    <br>

    <!--
        Progress bars for CPU usage and Memory
    -->
    <div class="row">
        <div class="container  col-lg-6 col-md-6 col-sm-12">
            <h4 id="status-cpu">Load: </h4>
            <div class="progress" style="height: 40px">
                <div class="progress-bar progress-bar-striped progress-bar-animated" id="status-bar-cpu" role="progressbar" style="width: 0%; height: 40px;" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        </div>
        <div class="container  col-lg-6 col-md-6 col-sm-12" >
            <h4 id="status-mem">Memory: </h4>
            <div class="progress" style="height: 40px">
                <div class="progress-bar progress-bar-striped progress-bar-animated" id="status-bar-mem" role="progressbar" style="width: 0%; height: 40px;" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        </div>
    </div>
    <br>

    <!--
        Shows processes that are running - Camera, GPS and Timing
    -->
    <div class="row">
        <h4 class="col-lg-4 col-md-4 col-sm-12">
            Camera  <span class="badge badge-dark"> Offline </span>
        </h4>
        <h4 class="col-lg-4 col-md-4 col-sm-12">
            GPS  <span class="badge badge-dark"> Offline </span>
        </h4>
        <h4 class="col-lg-4 col-md-4 col-sm-12">
            Timing  <span class="badge badge-dark"> Offline </span>
        </h4>
    </div>
    <br>

    <!--
        Table with all System Status
    -->
    <div class="table-responsive d-flex justify-content-center">
    <table class="table table-striped col-lg-10 col-md-12 col-sm-12">
            <thead>
                <tr>
                    <th>Property</th>
                    <th>Value</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Status</td>
                    <td id="status-status">Standby</td>
                    <td >
                        <a tabindex="0" role="button" class="btn btn-secondary" data-toggle="popover" data-trigger="focus" 
                        title="System status" 
                        data-content="One line with general status of the system">?</a>
                    </td>
                </tr>
                <tr>
                    <td>Last log</td>
                    <td id="status-log">Empty</td>
                    <td>
                        <a tabindex="0" role="button" class="btn btn-secondary" data-toggle="popover" data-trigger="focus" 
                        title="System log" 
                        data-content="Last entry in the log file">?</a>
                    </td>
                </tr>
                <tr>
                    <td>Reconding time</td>
                    <td id="status-rec-time">0</td>
                    <td>
                        <a tabindex="0" role="button" class="btn btn-secondary" data-toggle="popover" data-trigger="focus" 
                        title="Recording counter" 
                        data-content="Counts since start of recording, 0 - not recording">?</a>
                    </td>
                </tr>
                <tr>
                    <td>Recording file</td>
                    <td id="status-rec-file">No file</td>
                    <td>
                        <a tabindex="0" role="button" class="btn btn-secondary" data-toggle="popover" data-trigger="focus" 
                        title="Filename" 
                        data-content="Name of the current recording file">?</a>
                    </td>
                </tr>
                <tr>
                    <td>GPS fix</td>
                    <td id="status-gps-fix">No fix</td>
                    <td>
                        <a tabindex="0" role="button" class="btn btn-secondary" data-toggle="popover" data-trigger="focus" 
                        title="GPS status" 
                        data-content="if GPS is enabled, shows if a position fix is established">?</a>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <br>

    <!--
        Progress bars for Battery
    -->
    <div class="row">
        <div class="container col-lg-6 col-md-6 col-sm-12 justify-content-left">
            <h4 id="status-cpu">Battery Voltage: </h4>
            <div class="progress" style="height: 40px">
                <div class="progress-bar progress-bar-striped progress-bar-animated" id="status-bar-bat" role="progressbar" style="width: 0%; height: 40px;" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        </div>
    </div>

</main>

<?php
  require "footer.php";
?>