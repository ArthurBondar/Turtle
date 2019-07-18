<?php
  require "header.php";
?>

<main role="main" class="col-md-12 ml-sm-auto col-lg-12 px-4">

    <!--
        Label
    -->
    <h2 class="col-md-12 col-sm-12 col-lg-12">Configuration</h2>
    <br>

    <!--
        System configuration
    -->
    <div class="table-responsive d-flex justify-content-center">
        <table class="table table-striped col-lg-12 col-md-12 col-sm-12">
            <thead>
                <tr>
                    <th>Property</th>
                    <th>Value</th>
                    <th>New Value</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Start recording</td>
                    <td id="config-rec-start">Empty</td>
                    <td >

                    </td>
                </tr>
                <tr>
                    <td>End recording</td>
                      <td id="config-rec-end">Empty</td>
                      <td >

                    </td>
                </tr>
                <tr>
                    <td>Video sections</td>
                      <td id="config-rec-sec">Empty</td>
                      <td >

                    </td>
                </tr>
                <tr>
                    <td>Resolution</td>
                    <td id="status-resolution">Empty</td>
                    <td>
                        
                    </td>
                </tr>
                <tr>
                    <td>Frames per second</td>
                    <td id="status-fps">Empty</td>
                    <td>
                        
                    </td>
                </tr>
                <tr>
                    <td>Camera rotation</td>
                    <td id="status-rot">Empty</td>
                    <td>
                       
                    </td>
                </tr>
                <tr>
                    <td>GPS enable</td>
                    <td id="status-gps-en">Empty</td>
                    <td>
                      <div class="btn-group btn-group-toggle" data-toggle="buttons">
                        <label class="btn btn-success btn-sm active">
                          <input type="radio" name="options" id="btn-gps-en" autocomplete="off"> Enable
                        </label>
                        <label class="btn btn-danger btn-sm">
                          <input type="radio" name="options" id="btn-gps-dis" autocomplete="off"> Disable
                        </label>
                      </div>
                    </td>
                </tr>
                <tr>
                    <td>GPS interval</td>
                    <td id="status-gps-int">Empty</td>
                    <td>
                       
                    </td>
                </tr>
            </tbody>
        </table>
    </div>


</main>



<?php
  require "footer.php";
?>