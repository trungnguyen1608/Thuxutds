<?php
include('../PHP_OPTION/DB.php');
include('../cURL.php');

echo '<script>
toastr.options = {
  "closeButton": false,
  "debug": false,
  "newestOnTop": false,
  "progressBar": false,
  "positionClass": "toastr-top-right",
  "preventDuplicates": false,
  "onclick": null,
  "showDuration": "300",
  "hideDuration": "1000",
  "timeOut": "5000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
};
</script>';

$id = $_POST['idgoi'];
$getTheme = mysqli_fetch_array(mysqli_query($connect, "SELECT * FROM DanhSachTheme WHERE id = '$id'"));
$mien = $_POST['domainname'];
$domain = $_POST['domain'];
$taikhoan = $getTheme['taikhoan'];
$matkhau = $getTheme['matkhau'];
$handung = $_POST['handung'];
$getDomain = mysqli_fetch_array(mysqli_query($connect, "SELECT * FROM TrangWeb WHERE domain = '$mien.$mien'"));
$tongmien = $mien.$domain;
        
$timeout = time()+(86400*$nhan);
        
        
if($_POST['domainname'] == "" || $_POST['domain'] == "" || $handung == ""){
 echo '<script>toastr.error("Vui Lòng Nhập Đầy Đủ Thông Tin!", "Thông Báo");</script>';
} else {
    
    if($getUser['monney'] > $getTheme['price'] * $handung){
   
        if($getTheme['loaitao'] == 'true'){
        $filezip = $getTheme['code'];
        $filesql = $getTheme['sql'];
            
      
           $parameters = [
            'domain' => $mien,
            'rootdomain' => $configdomain,
            'dir' => '/'.$mien.$domain,
            'disallowdot' => 1,
        ];
            $result = $cPanel->execute('api2',"SubDomain", "addsubdomain" , $parameters);
           
    
        $thongtin = [ 'name' => $ushost.'_'.$mien, 'password' => $ushost.'_'.$mien ];
        $result1 = $cPanel->execute('uapi', 'Mysql', 'create_user', $thongtin);
        
        $thongtin1 = [ 'name' => $ushost.'_'.$mien ];
        $result2 = $cPanel->execute('uapi', 'Mysql', 'create_database', $thongtin1);
         
        $thongtin2 = [ 'user' => $ushost.'_'.$mien, 'database' => $ushost.'_'.$mien, 'privileges' => 'ALL PRIVILEGES' ];
        $result3 = $cPanel->execute('uapi', 'Mysql', 'set_privileges_on_database', $thongtin2);
        
        
        file_put_contents('/home/'.$ushost.'/'.$mien.$domain.'/'.$mien.'.zip', file_get_contents($filezip));
    
    
             $hanhcotdoit = new ZipArchive();
             
            $file = '/home/'.$ushost.'/'.$mien.$domain.'/'.$mien.'.zip';
            $path = pathinfo(realpath($file), PATHINFO_DIRNAME);
           
            $res = $hanhcotdoit->open($file);
            if ($res === TRUE)
            {
                $hanhcotdoit->extractTo($path);
                $hanhcotdoit->close();
                unlink($file);
            }
    
          $sql = file_get_contents($filesql);
          $mysqli = new mysqli("localhost", $ushost.'_'.$mien, $ushost.'_'.$mien, $ushost.'_'.$mien);
          /* execute multi query */
          $mysqli->multi_query($sql);
          
    
          $file = ('/home/doicard4/'.$mien.$domain.'/config.txt');
          $data = 'doicard4'.$mien;
          file_put_contents($file, $data);
      
        $doicard4re = mysqli_query($connect, "INSERT INTO `TrangWeb`(`id`, `taikhoan`, `matkhau`, `theme`, `domain`, `status`, `time`, `timeout`, `username`) VALUES ('NULL', '$taikhoan', '$matkhau', '$id', '$tongmien', '1', '$time', '$timeout', '".$getUser['username']."')");      
        if($doicard4re){
            
                echo '<script>toastr.success("Tạo Trang Web Thành Công!", "Thông Báo");</script>';
                mysqli_query($connect, "UPDATE Users SET monney = monney - '".$getTheme['price'] * $handung."', tongtieu = tongtieu + '".$getTheme['price'] * $handung."' WHERE id = '".$getUser['id']."'");
                
        } else {
            
                echo '<script>toastr.success("Tạo Thất Bại!", "Thông Báo");</script>';
        }
                
        } else {
        
          
        }
    
    } else {
         echo '<script>toastr.error("Không Đủ Số Dư Để Thanh Toán!", "Thông Báo");</script>';
    }
    
} 
?>