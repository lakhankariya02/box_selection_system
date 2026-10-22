# Test Output

Command (Windows, Python 3.12.x, inside the venv):

```powershell
python manage.py test -v 2
```

Result: **30 tests, all passing.**

```text
.\venv\Scripts\python.exe : Creating test database for alias 'default' 
('file:memorydb_default?mode=memory&cache=shared')...
At line:1 char:302
+ ... tch {} } }; .\venv\Scripts\python.exe manage.py test -v 2 *> test_run ...
+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (Creating test d...che=shared')...:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 

Found 30 test(s).
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, contenttypes, sessions, shipping
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
test_create_order_then_recommend (shipping.tests.test_api.ApiTests.test_create_order_then_recommend) ... ok
test_product_crud (shipping.tests.test_api.ApiTests.test_product_crud) ... ok
test_product_zero_dimension_rejected (shipping.tests.test_api.ApiTests.test_product_zero_dimension_rejected) ... ok
test_recommend_duplicate_sku_rejected (shipping.tests.test_api.ApiTests.test_recommend_duplicate_sku_rejected) ... ok
test_recommend_empty_items_rejected (shipping.tests.test_api.ApiTests.test_recommend_empty_items_rejected) ... ok
test_recommend_endpoint (shipping.tests.test_api.ApiTests.test_recommend_endpoint) ... ok
test_recommend_nothing_fits (shipping.tests.test_api.ApiTests.test_recommend_nothing_fits) ... ok
test_recommend_unknown_sku (shipping.tests.test_api.ApiTests.test_recommend_unknown_sku) ... ok
test_recommend_zero_quantity_rejected (shipping.tests.test_api.ApiTests.test_recommend_zero_quantity_rejected) ... ok
test_empty_order_raises (shipping.tests.test_services.RecommendBoxTests.test_empty_order_raises) ... ok
test_inactive_box_is_ignored (shipping.tests.test_services.RecommendBoxTests.test_inactive_box_is_ignored) ... ok
test_long_item_chooses_long_box_not_largest 
(shipping.tests.test_services.RecommendBoxTests.test_long_item_chooses_long_box_not_largest) ... ok
test_mixed_order_totals (shipping.tests.test_services.RecommendBoxTests.test_mixed_order_totals) ... ok
test_no_box_fits (shipping.tests.test_services.RecommendBoxTests.test_no_box_fits) ... ok
test_picks_cheapest_box_that_fits (shipping.tests.test_services.RecommendBoxTests.test_picks_cheapest_box_that_fits) 
... ok
test_quantity_pushes_to_bigger_box (shipping.tests.test_services.RecommendBoxTests.test_quantity_pushes_to_bigger_box) 
... ok
test_recommend_for_order_saves_box (shipping.tests.test_services.RecommendBoxTests.test_recommend_for_order_saves_box) 
... ok
test_same_cost_prefers_smaller_box (shipping.tests.test_services.RecommendBoxTests.test_same_cost_prefers_smaller_box) 
... ok
test_weight_limit_rejects_box_that_is_big_enough 
(shipping.tests.test_services.RecommendBoxTests.test_weight_limit_rejects_box_that_is_big_enough) ... ok
test_zero_quantity_raises (shipping.tests.test_services.RecommendBoxTests.test_zero_quantity_raises) ... ok
test_exact_fit (shipping.tests.test_packing.FitsIndividuallyTests.test_exact_fit) ... ok
test_fits_only_when_rotated (shipping.tests.test_packing.FitsIndividuallyTests.test_fits_only_when_rotated) ... ok
test_too_long_in_every_orientation 
(shipping.tests.test_packing.FitsIndividuallyTests.test_too_long_in_every_orientation) ... ok
test_eight_cubes_fill_box_exactly (shipping.tests.test_packing.PackTests.test_eight_cubes_fill_box_exactly) ... ok
test_mixed_sizes (shipping.tests.test_packing.PackTests.test_mixed_sizes) ... ok
test_needs_rotation_to_pack_two_items (shipping.tests.test_packing.PackTests.test_needs_rotation_to_pack_two_items) 
... ok
test_ninth_cube_does_not_fit (shipping.tests.test_packing.PackTests.test_ninth_cube_does_not_fit) ... ok
test_placements_are_inside_box_and_never_overlap 
(shipping.tests.test_packing.PackTests.test_placements_are_inside_box_and_never_overlap)
Property check: whatever the packer places must be physically valid. ... ok
test_single_item (shipping.tests.test_packing.PackTests.test_single_item) ... ok
test_volume_is_enough_but_shape_is_not (shipping.tests.test_packing.PackTests.test_volume_is_enough_but_shape_is_not) 
... ok

----------------------------------------------------------------------
Ran 30 tests in 0.152s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...

  Applying shipping.0001_initial... OK
System check identified no issues (0 silenced).
```
