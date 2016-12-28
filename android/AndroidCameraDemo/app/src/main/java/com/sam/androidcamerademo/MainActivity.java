package com.sam.androidcamerademo;

import android.content.pm.ActivityInfo;
import android.graphics.ImageFormat;
import android.hardware.Camera;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.Window;
import android.view.WindowManager;

public class MainActivity extends AppCompatActivity {

    static final String TAG = "AndroidCameraDemo";

    private SurfaceView mSurfaceView;
    private Camera mCamera;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);

        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);

        getWindow().setFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);

        setContentView(R.layout.activity_main);

        mSurfaceView = (SurfaceView) findViewById(R.id.surfaceView);

        mSurfaceView.getHolder().setKeepScreenOn(true);

        mSurfaceView.getHolder().addCallback(new SurfaceHolder.Callback() {
            @Override
            public void surfaceCreated(SurfaceHolder holder) {
                try {
                    mCamera = Camera.open(0);
                    Camera.Parameters param = mCamera.getParameters();
                    param.setPreviewSize(1280, 720);
                    param.setPreviewFpsRange(10, 20);
                    param.setPictureFormat(ImageFormat.JPEG);
                    param.setPictureSize(1280, 720);
                    param.setJpegQuality(80);
                    mCamera.setParameters(param);

                    param = mCamera.getParameters();
                    Log.v(TAG, "open camera " + param.getPreviewSize().width + "x" + param.getPreviewSize().height);

                    mCamera.setPreviewDisplay(holder);
                    mCamera.startPreview();
                } catch (Exception err) {
                    err.printStackTrace();
                    if (mCamera != null) {
                        mCamera.release();
                        mCamera = null;
                    }
                }
            }

            @Override
            public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) {
            }

            @Override
            public void surfaceDestroyed(SurfaceHolder holder) {
                if (mCamera != null) {
                    mCamera.stopPreview();
                    mCamera.release();
                    mCamera = null;
                }
            }
        });
    }

}
