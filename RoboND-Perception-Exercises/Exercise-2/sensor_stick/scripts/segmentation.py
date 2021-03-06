#!/usr/bin/env python

# Import modules
from pcl_helper import *

# TODO: Define functions as required

# Callback function for your Point Cloud Subscriber
def pcl_callback(pcl_msg):

    # TODO: Convert ROS msg to PCL data
	pcl_data = ros_to_pcl(pcl_msg)

    # TODO: Voxel Grid Downsampling
	cloud = pcl_data
	# Create a VoxelGrid filter object for our input point cloud
	vox = cloud.make_voxel_grid_filter()

	# Choose a voxel (also known as leaf) size
	
	LEAF_SIZE = 0.01   

	# Set the voxel (or leaf) size  
	vox.set_leaf_size(LEAF_SIZE, LEAF_SIZE, LEAF_SIZE)

	# Call the filter function to obtain the resultant downsampled point cloud
	cloud_filtered = vox.filter()
	filename = 'voxel_downsampled.pcd'
	pcl.save(cloud_filtered, filename)

    # TODO: PassThrough Filter
		# Create a PassThrough filter object.
	passthrough = cloud_filtered.make_passthrough_filter()

	# Assign axis and range to the passthrough filter object.
	filter_axis = 'z'
	passthrough.set_filter_field_name(filter_axis)
	axis_min = 0.77
	axis_max = 1.1
	passthrough.set_filter_limits(axis_min, axis_max)

	# Finally use the filter function to obtain the resultant point cloud. 
	cloud_filtered = passthrough.filter()
	filename = 'pass_through_filtered.pcd'
	pcl.save(cloud_filtered, filename)

    # TODO: RANSAC Plane Segmentation
		# Create the segmentation object
	seg = cloud_filtered.make_segmenter()

	# Set the model you wish to fit 
	seg.set_model_type(pcl.SACMODEL_PLANE)
	seg.set_method_type(pcl.SAC_RANSAC)

	# Max distance for a point to be considered fitting the model
	
	max_distance = 0.01
	seg.set_distance_threshold(max_distance)

	# Call the segment function to obtain set of inlier indices and model coefficients
	inliers, coefficients = seg.segment()

    # TODO: Extract inliers and outliers

	# Extract inliers
	extracted_inliers = cloud_filtered.extract(inliers, negative=False)			# pcd for table
	filename = 'extracted_inliers.pcd'
	pcl.save(extracted_inliers, filename)
	
	# Extract outliers
	extracted_outliers = cloud_filtered.extract(inliers, negative=True)			# pcd for objects
	filename = 'extracted_outliers.pcd'
	pcl.save(extracted_outliers, filename)

    # TODO: Euclidean Clustering
	white_cloud = XYZRGB_to_XYZ(extracted_outliers)						# Apply function to convert XYZRGB to XYZ
	tree = white_cloud.make_kdtree()

    # TODO: Create Cluster-Mask Point Cloud to visualize each cluster separately
		# Create a cluster extraction object
	ec = white_cloud.make_EuclideanClusterExtraction()
	# Set tolerances for distance threshold 
	# as well as minimum and maximum cluster size (in points)
	
	ec.set_ClusterTolerance(0.02)
	ec.set_MinClusterSize(50)
	ec.set_MaxClusterSize(1700)
	# Search the k-d tree for clusters
	ec.set_SearchMethod(tree)
	# Extract indices for each of the discovered clusters
	cluster_indices = ec.Extract()
	
	#Assign a color corresponding to each segmented object in scene
	cluster_color = get_color_list(len(cluster_indices))

	color_cluster_point_list = []

	for j, indices in enumerate(cluster_indices):
	    for i, indice in enumerate(indices):
		color_cluster_point_list.append([white_cloud[indice][0],
		                                white_cloud[indice][1],
		                                white_cloud[indice][2],
		                                 rgb_to_float(cluster_color[j])])

	#Create new cloud containing all clusters, each with unique color
	cluster_cloud = pcl.PointCloud_PointXYZRGB()
	cluster_cloud.from_list(color_cluster_point_list)

    # TODO: Convert PCL data to ROS messages	
	ros_cloud_objects = pcl_to_ros(extracted_outliers) 			# Conversion to ROS messages for ALL Object Point Cloud
	ros_cloud_table = pcl_to_ros(extracted_inliers)				# Conversion to ROS messages for Table Point Cloud
	ros_cluster_cloud = pcl_to_ros(cluster_cloud)				# Conversion to ROS messages for INDIVIDUAL Object Point Cloud

    # TODO: Publish ROS messages
	pcl_objects_pub.publish(ros_cloud_objects)
	pcl_table_pub.publish(ros_cloud_table)
	pcl_cluster_pub.publish(ros_cluster_cloud)

if __name__ == '__main__':

    # TODO: ROS node initialization
	rospy.init_node('clustering', anonymous=True)

    # TODO: Create Subscribers
	pcl_sub = rospy.Subscriber("/sensor_stick/point_cloud", pc2.PointCloud2, pcl_callback, queue_size=1)

    # TODO: Create Publishers
	pcl_objects_pub = rospy.Publisher("/pcl_objects", PointCloud2, queue_size=1)
	pcl_table_pub = rospy.Publisher("/pcl_table", PointCloud2, queue_size=1)
	pcl_cluster_pub = rospy.Publisher("/pcl_cluster", PointCloud2, queue_size=1)

    # Initialize color_list
    	get_color_list.color_list = []

    # TODO: Spin while node is not shutdown
	while not rospy.is_shutdown():
 		rospy.spin()

